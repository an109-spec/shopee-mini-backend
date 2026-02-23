from decimal import Decimal
from secrets import token_hex
from urllib.parse import urlparse

from werkzeug.security import check_password_hash, generate_password_hash

from app.common.exceptions import ConflictError, NotFoundError, ValidationError
from app.extensions import db
from app.models import Order, OrderItem, Product, User, UserProfile


class UserService:
    AVATAR_STYLES = ("avataaars", "bottts", "identicon", "micah", "notionists")

    @staticmethod
    def _get_user(user_id: int) -> User:
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundError("Không tìm thấy người dùng")
        return user

    @staticmethod
    def _decimal_to_string(value: Decimal | None) -> str:
        if value is None:
            return "0"
        return str(value)

    @staticmethod
    def _build_random_avatar_url() -> str:
        seed = token_hex(8)
        style = UserService.AVATAR_STYLES[int(seed[0], 16) % len(UserService.AVATAR_STYLES)]
        return f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}"

    @staticmethod
    def _validate_avatar_url(avatar_url: str) -> str:
        if not avatar_url or not avatar_url.strip():
            raise ValidationError("Avatar không được để trống")

        avatar_url = avatar_url.strip()
        parsed = urlparse(avatar_url)

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValidationError("Avatar phải là URL hợp lệ")

        return avatar_url

    @staticmethod
    def ensure_auto_avatar(user_id: int) -> str:
        user = UserService._get_user(user_id)

        if user.avatar and user.avatar.strip():
            return user.avatar

        avatar_url = UserService._build_random_avatar_url()
        with db.session.begin():
            user.avatar = avatar_url
        return avatar_url

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
                "gender": profile.gender if profile else None,
                "birthday": profile.birthday.isoformat() if profile and profile.birthday else None,
            },
        }

    @staticmethod
    def change_avatar(user_id: int, avatar_url: str) -> str:
        avatar_url = UserService._validate_avatar_url(avatar_url)
        user = UserService._get_user(user_id)

        with db.session.begin():
            user.avatar = avatar_url

        return avatar_url

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

        with db.session.begin():
            user.password_hash = generate_password_hash(new_password)
            user.failed_login_attempts = 0
            user.locked_until = None

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

        product_ids = {item.product_id for item in order_items if item.product_id is not None}
        products = Product.query.filter(Product.id.in_(product_ids)).all() if product_ids else []
        product_by_id = {product.id: product for product in products}

        items_by_order_id: dict[int, list[OrderItem]] = {order_id: [] for order_id in order_ids}
        for item in order_items:
            items_by_order_id.setdefault(item.order_id, []).append(item)

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
                        "product_name": product.name if product else None,
                        "quantity": quantity,
                        "price": UserService._decimal_to_string(price),
                        "line_total": UserService._decimal_to_string(price * quantity),
                    }
                )

            result.append(
                {
                    "order_id": order.id,
                    "status": order.status,
                    "payment_method": order.payment_method,
                    "total_price": UserService._decimal_to_string(order.total_price),
                    "created_at": order.created_at.isoformat() if order.created_at else None,
                    "items": items_data,
                }
            )

        return result