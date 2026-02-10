import re
from app.common.exceptions import BadRequestError


EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def validate_email(email: str) -> None:
    if not email or not re.match(EMAIL_REGEX, email):
        raise BadRequestError("Email không hợp lệ")


def validate_password(password: str) -> None:
    if not password or len(password) < 6:
        raise BadRequestError("Mật khẩu tối thiểu 6 ký tự")


def validate_register(data: dict) -> None:
    validate_email(data.get("email"))
    validate_password(data.get("password"))

    if not data.get("full_name"):
        raise BadRequestError("Thiếu họ tên")


def validate_login(data: dict) -> None:
    validate_email(data.get("email"))

    if not data.get("password"):
        raise BadRequestError("Thiếu mật khẩu")
