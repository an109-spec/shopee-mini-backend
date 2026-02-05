from functools import wraps
from app.common.exceptions import ForbiddenError


def require_role(*roles: str):
    """
    Decorator kiểm tra user có thuộc một trong các role được phép hay không.
    Giả định: hàm được decorate có tham số `user` ở vị trí đầu tiên.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            if user is None or user.role not in roles:
                raise ForbiddenError("Permission denied")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator

