from functools import wraps
from app.common.exceptions import ForbiddenError
from app.models import User
from flask import session

def require_role(*roles: str):
    """
    Decorator kiểm tra user có thuộc một trong các role được phép hay không.
    Giả định: hàm được decorate có tham số `user` ở vị trí đầu tiên.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            if user is None or user.role not in roles:
                raise ForbiddenError("Permission denied")#từ chối quyền truy cập
            return func(user, *args, **kwargs)
        return wrapper
    return decorator


# @require_role("admin")
# def delete_product(user, product_id):

#@require_role("admin", "editor") # Có thể truyền nhiều role nhờ dấu *roles
def seller_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        user_id = session.get("user_id")

        if not user_id:
            raise ForbiddenError("Login required")

        user = User.query.get(user_id)

        if user.role not in ["seller","admin"]:
            raise ForbiddenError("Seller permission required")

        return func(*args, **kwargs)

    return wrapper


