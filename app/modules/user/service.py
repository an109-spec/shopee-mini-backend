from datetime import date
from decimal import Decimal
from hashlib import sha256
from urllib.parse import urlparse

from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from app.common.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
    AppException,
)
from app.extensions import db
from app.models import Order, OrderItem, Product, User, UserProfile


class UserService:
    AVATAR_STYLES = ("avataaars", "bottts", "identicon", "micah", "notionists")

    # ==============================
    # INTERNAL HELPERS
    # ==============================

    @staticmethod
    def _get_user(user_id: int) -> User:
        try:
            user = db.session.get(User, user_id)
        except SQLAlchemyError:
            raise AppException("Lỗi hệ thống cơ sở dữ liệu", status_code=500)

        if not user:
            raise NotFoundError("Không tìm thấy người dùng")

        return user

    @staticmethod
    def _decimal_to_string(value: Decimal | None) -> str:
        if value is None:
            return "0"
        return str(value)

    @staticmethod
    def _validate_avatar_url(avatar_url: str) -> str:
        if not avatar_url or not avatar_url.strip():
            raise ValidationError("Avatar không được để trống")

        avatar_url = avatar_url.strip()

        if len(avatar_url) > 500:
            raise ValidationError("URL avatar quá dài")

        parsed = urlparse(avatar_url)

        if parsed.scheme not in {"http", "https"}:
            raise ValidationError("Avatar phải dùng http hoặc https")

        if not parsed.netloc:
            raise ValidationError("Avatar phải là URL hợp lệ")

        if not parsed.path.lower().endswith(
            (".png", ".jpg", ".jpeg", ".webp", ".svg")
        ):
            raise ValidationError("Avatar phải là file ảnh hợp lệ")

        return avatar_url

    @staticmethod
    def change_avatar(user_id: int, avatar_url: str) -> str:
        avatar_url = UserService._validate_avatar_url(avatar_url)
        user = UserService._get_user(user_id)
        user.avatar = avatar_url
        db.session.commit()

        return avatar_url
    # ==============================
    # PROFILE
    # ==============================

    @staticmethod
    def get_profile(user_id: int) -> dict:
        user = UserService._get_user(user_id)
        profile = UserProfile.query.filter_by(user_id=user.id).first()

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "avatar": user.avatar,
            "role": user.role,
            "profile": {
                "full_name": profile.full_name if profile else None,
                "address": profile.address if profile else None,
                "addresses": [item for item in (profile.address or "").split("\n") if item.strip()] if profile else [],
                "gender": profile.gender if profile else None,
                "birthday": profile.birthday.isoformat() if profile and profile.birthday else None,
            },
        }

    @staticmethod
    def update_profile(user_id: int, payload: dict) -> dict:
        user = UserService._get_user(user_id)
        profile = UserProfile.query.filter_by(user_id=user.id).first()

        if profile is None:
            profile = UserProfile(user_id=user.id)
            db.session.add(profile)

        username = (payload.get("username") or "").strip()
        email = (payload.get("email") or "").strip().lower()
        phone = (payload.get("phone") or "").strip()
        full_name = (payload.get("full_name") or "").strip()
        birthday_raw = (payload.get("birthday") or "").strip()
        addresses_provided = "addresses" in payload
        addresses = payload.get("addresses") if addresses_provided else None

        if username:
            conflict = User.query.filter(User.username == username, User.id != user.id).first()
            if conflict:
                raise ConflictError("Username đã tồn tại")
            user.username = username

        if email:
            conflict = User.query.filter(User.email == email, User.id != user.id).first()
            if conflict:
                raise ConflictError("Email đã tồn tại")
            user.email = email

        if phone:
            conflict = User.query.filter(User.phone == phone, User.id != user.id).first()
            if conflict:
                raise ConflictError("Số điện thoại đã tồn tại")
            user.phone = phone

        if full_name:
            profile.full_name = full_name

        if birthday_raw:
            try:
                profile.birthday = date.fromisoformat(birthday_raw)
            except ValueError:
                raise ValidationError("Ngày sinh không hợp lệ, dùng định dạng YYYY-MM-DD")

        if addresses_provided:
            if not isinstance(addresses, list):
                raise ValidationError("Danh sách địa chỉ không hợp lệ")
            cleaned = [str(item).strip() for item in addresses if str(item).strip()]
            profile.address = "\n".join(cleaned)

        db.session.commit()
        return UserService.get_profile(user.id)

    @staticmethod
    def set_avatar_file(user_id: int, avatar_path: str) -> str:
        user = UserService._get_user(user_id)
        user.avatar = avatar_path
        db.session.commit()
        return avatar_path

    # ==============================
    # PASSWORD
    # ==============================

    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> None:
        if not current_password or not new_password:
            raise ValidationError("Thiếu thông tin đổi mật khẩu")

        if len(new_password) < 8:
            raise ValidationError("Mật khẩu mới phải tối thiểu 8 ký tự")

        user = UserService._get_user(user_id)

        if not check_password_hash(user.password_hash, current_password):
            raise ConflictError("Mật khẩu hiện tại không đúng")

        if check_password_hash(user.password_hash, new_password):
            raise ConflictError("Mật khẩu mới không được trùng mật khẩu cũ")
        user.password_hash = generate_password_hash(new_password)
        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()
    # ==============================
    # PURCHASE HISTORY
    # ==============================

    @staticmethod
    def purchase_history(user_id: int) -> list[dict]:
        UserService._get_user(user_id)

        orders = (
            Order.query.filter_by(user_id=user_id)
            .order_by(Order.created_at.desc())
            .all()
        )

        if not orders:
            return []

        order_ids = [order.id for order in orders]

        order_items = (
            OrderItem.query
            .filter(OrderItem.order_id.in_(order_ids))
            .all()
        )

        product_ids = {
            item.product_id
            for item in order_items
            if item.product_id is not None
        }

        products = (
            Product.query.filter(Product.id.in_(product_ids)).all()
            if product_ids
            else []
        )

        product_by_id = {product.id: product for product in products}

        items_by_order_id: dict[int, list[OrderItem]] = {
            order_id: [] for order_id in order_ids
        }

        for item in order_items:
            items_by_order_id.setdefault(
                item.order_id, []
            ).append(item)

        result = []

        for order in orders:
            items_data = []

            for item in items_by_order_id.get(order.id, []):
                product = product_by_id.get(item.product_id)
                quantity = item.quantity or 0
                price = item.price or Decimal("0")

                items_data.append(
                    {
                        "product_id": item.product_id,
                        "product_name": product.name
                        if product
                        else None,
                        "quantity": quantity,
                        "price": UserService._decimal_to_string(price),
                        "line_total": UserService._decimal_to_string(
                            price * quantity
                        ),
                    }
                )

            result.append(
                {
                    "order_id": order.id,
                    "status": order.status,
                    "payment_method": order.payment_method,
                    "total_price": UserService._decimal_to_string(
                        order.total_price
                    ),
                    "created_at": order.created_at.isoformat()
                    if order.created_at
                    else None,
                    "items": items_data,
                }
            )

        return result