from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.common.exceptions import UnauthorizedError, ForbiddenError
from app.models.user import User
from flask import g

def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        if not user_id:
            raise UnauthorizedError("Authentication required")

        user = User.query.get(user_id)
        if not user:
            raise UnauthorizedError("User not found")

        g.user = user  

        return fn(*args, **kwargs)
    return wrapper

def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, "user", None)
            if not user:
                raise UnauthorizedError("Authentication required")

            if user.role not in roles:
                raise ForbiddenError("Permission denied")

            return fn(*args, **kwargs)
        return wrapper
    return decorator



def deco(fn):
    @wraps(fn)
    def wrap(*args, **kwargs):
        user_id=get_jwt_identity()
        if not user_id:
            raise UnauthorizedError("Authentication required")
        user=User.query.get(user_id)
        if not user:
            raise UnauthorizedError("user not found")
        g.user=user
        return fn(*args, **kwargs)
    return wrap

def auth_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrap(*args, **kwargs):
            user=getattr(g, "user", None)
            if not user:
                raise UnauthorizedError("Authentication required")
            if not user.role not in roles:
                raise ForbiddenError("permission denied")
            return fn(*args, **kwargs)
        return wrap
    return deco
