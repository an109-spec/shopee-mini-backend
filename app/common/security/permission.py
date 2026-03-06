from functools import wraps
from flask import session
from app.models import User
from app.common.exceptions import ForbiddenError


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
    return require_role("seller", "admin")(func)


def admin_required(func):
    return require_role("admin")(func)