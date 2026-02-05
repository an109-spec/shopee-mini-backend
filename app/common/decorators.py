from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.common.exceptions import UnauthorizedError
from app.models.user import User


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        if not user_id:
            raise UnauthorizedError()
        return fn(*args, **kwargs)
    return wrapper


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            if not user_id:
                raise UnauthorizedError()

            user = User.query.get(user_id)
            if user.role not in roles:
                from app.common.exceptions import ForbiddenError
                raise ForbiddenError()

            return fn(*args, **kwargs)
        return wrapper
    return decorator
