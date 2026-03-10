from functools import wraps
from flask import session, redirect, url_for, flash 
from app.common.exceptions import ForbiddenError
from app.models import User, Shop

def require_role(*roles: str):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            user_id = session.get("user_id")

            if not user_id:
                raise ForbiddenError("Login required")

            user = User.query.get(user_id)

            if not user:
                raise ForbiddenError("User not found")

            if user.role not in roles:
                raise ForbiddenError("Permission denied")

            return func(*args, **kwargs)

        return wrapper

    return decorator

def seller_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        user_id = session.get("user_id")

        # chưa login
        if not user_id:
            return redirect(url_for("auth.login", role="seller"))

        user = User.query.get(user_id)

        if not user:
            return redirect(url_for("auth.login", role="seller"))

        shop = Shop.query.filter_by(owner_id=user.id).first()

        if not shop:
            flash("Bạn cần đăng ký người bán để truy cập kênh người bán", "warning")
            return redirect(url_for("seller.register_shop"))
        if not user.is_seller:
            flash("Bạn cần đăng ký người bán để truy cập kênh người bán", "warning")
            return redirect(url_for("seller.register_shop"))

        if not shop.onboarding_completed:
            return redirect(url_for("seller.seller_center"))

        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    return require_role("admin")(func)