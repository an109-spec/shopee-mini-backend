import re
from app.common.exceptions import ValidationError


EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PHONE_PATTERN = re.compile(r"^\+?\d{9,15}$")


# =========================
# EMAIL
# =========================
def validate_email(email: str) -> None:
    if email is None:
        raise ValidationError("Thiếu email")

    email = email.strip()

    if not email:
        raise ValidationError("Thiếu email")

    if not EMAIL_PATTERN.fullmatch(email):
        raise ValidationError("Email không hợp lệ")


# =========================
# PHONE
# =========================
def validate_phone(phone: str) -> None:
    if phone is None:
        raise ValidationError("Thiếu số điện thoại")

    phone = phone.strip()

    if not phone:
        raise ValidationError("Thiếu số điện thoại")

    if not PHONE_PATTERN.fullmatch(phone):
        raise ValidationError("Số điện thoại không hợp lệ")


# =========================
# PASSWORD
# =========================
def validate_password(password: str) -> None:
    if password is None:
        raise ValidationError("Thiếu mật khẩu")

    password = password.strip()

    if not password:
        raise ValidationError("Thiếu mật khẩu")

    if len(password) < 8:
        raise ValidationError("Mật khẩu tối thiểu 8 ký tự")


# =========================
# REGISTER
# =========================
def validate_register(data: dict) -> list[str]:
    errors = []

    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    full_name = data.get("full_name")

    # Phải có ít nhất 1 trong 2
    if not email and not phone:
        errors.append("Phải nhập email hoặc số điện thoại")

    # Nếu có email thì validate
    if email:
        try:
            validate_email(email)
        except ValidationError as e:
            errors.append(str(e))

    # Nếu có phone thì validate
    if phone:
        try:
            validate_phone(phone)
        except ValidationError as e:
            errors.append(str(e))

    # Password
    try:
        validate_password(password)
    except ValidationError as e:
        errors.append(str(e))

    if not full_name or not full_name.strip():
        errors.append("Thiếu họ tên")

    return errors


# =========================
# LOGIN
# =========================
def validate_login(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValidationError("Dữ liệu không hợp lệ")

    identifier = data.get("identifier")
    password = data.get("password")

    if not identifier or not identifier.strip():
        raise ValidationError("Thiếu email hoặc số điện thoại")

    if not password or not password.strip():
        raise ValidationError("Thiếu mật khẩu")