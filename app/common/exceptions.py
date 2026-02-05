class AppException(Exception):
    """Base exception cho toàn hệ thống"""
    status_code = 400
    message = "Application error"

    def __init__(self, message=None, status_code=None):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AppException):
    status_code = 422
    message = "Validation error"


class UnauthorizedError(AppException):
    status_code = 401
    message = "Unauthorized"


class ForbiddenError(AppException):
    status_code = 403
    message = "Forbidden"


class NotFoundError(AppException):
    status_code = 404
    message = "Resource not found"


class ConflictError(AppException):
    status_code = 409
    message = "Conflict"
