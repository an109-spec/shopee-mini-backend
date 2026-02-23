from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from app.models import User
from app.extensions import db
from app.common.exceptions import (
    UnauthorizedError,
    ConflictError,
    ValidationError
)

from .dto import LoginDTO, RegisterDTO, RequestPasswordResetDTO, ResetPasswordDTO
from .otp_service import OTPService
from .sms_service import SMSService


class AuthService:

    # ======================================================
    # UTIL
    # ======================================================

    @staticmethod
    def _normalize_identifier(identifier: str) -> str:
        if not identifier or not identifier.strip():
            raise ValidationError("Thiếu email hoặc số điện thoại")

        identifier = identifier.strip()

        # Nếu là email thì lower
        if "@" in identifier:
            return identifier.lower()

        # Phone giữ nguyên
        return identifier

    @staticmethod
    def _get_user_by_identifier(identifier: str) -> User | None:
        return User.query.filter(
            or_(
                User.email == identifier,
                User.phone == identifier
            )
        ).first()

    # ======================================================
    # REGISTER
    # ======================================================

    @staticmethod
    def register(dto: RegisterDTO) -> User:

        if not dto.email and not dto.phone:
            raise ValidationError("Phải cung cấp email hoặc số điện thoại")

        user = User(
            email=dto.email.lower().strip() if dto.email else None,
            phone=dto.phone.strip() if dto.phone else None,
            password_hash=generate_password_hash(dto.password),
            full_name=dto.full_name.strip(),
        )

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ConflictError("Email hoặc số điện thoại đã tồn tại")

        return user

    # ======================================================
    # LOGIN
    # ======================================================

    @staticmethod
    def login(dto: LoginDTO) -> User:

        identifier = AuthService._normalize_identifier(dto.identifier)
        user = AuthService._get_user_by_identifier(identifier)

        # Không tiết lộ user tồn tại
        if not user:
            raise UnauthorizedError("Sai thông tin đăng nhập")

        now = datetime.now(timezone.utc)

        # ===== Check lock =====
        if user.locked_until and user.locked_until > now:
            raise UnauthorizedError(
                message="Tài khoản bị khóa",
                locked_until=user.locked_until
            )

        # ===== Check password =====
        if not check_password_hash(user.password_hash, dto.password):
            user.failed_login_attempts += 1
            user.last_failed_login = now

            if user.failed_login_attempts >= 5:
                user.locked_until = now + timedelta(minutes=15)

            db.session.commit()
            raise UnauthorizedError("Sai thông tin đăng nhập")

        # ===== Login success =====
        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()

        return user

    # ======================================================
    # REQUEST PASSWORD RESET
    # ======================================================

    @staticmethod
    def request_password_reset(dto: RequestPasswordResetDTO) -> None:

        identifier = AuthService._normalize_identifier(dto.identifier)
        user = AuthService._get_user_by_identifier(identifier)

        # Không tiết lộ user tồn tại
        if not user:
            return

        # Nếu reset qua email
        if user.email:
            email_code = OTPService.create_otp(user.id, otp_type="email")
            # TODO: thay bằng email service thật
            print(f"[EMAIL OTP] {email_code}")

        # Nếu reset qua SMS
        if user.phone:
            sms_code = OTPService.create_otp(user.id, otp_type="sms")
            SMSService.send(
                user.phone,
                f"Mã OTP của bạn là {sms_code}"
            )

    # ======================================================
    # RESET PASSWORD
    # ======================================================

    @staticmethod
    def reset_password(dto: ResetPasswordDTO) -> None:

        identifier = AuthService._normalize_identifier(dto.identifier)
        user = AuthService._get_user_by_identifier(identifier)

        if not user:
            raise UnauthorizedError("OTP không hợp lệ")

        # ===== Verify OTP =====
        is_valid = OTPService.verify_otp(
            user_id=user.id,
            code=dto.otp_code,
            otp_type=dto.otp_type
        )

        if not is_valid:
            raise UnauthorizedError("OTP không hợp lệ hoặc đã hết hạn")

        # ===== Password policy =====
        if len(dto.new_password) < 8:
            raise ConflictError("Mật khẩu phải tối thiểu 8 ký tự")

        if check_password_hash(user.password_hash, dto.new_password):
            raise ConflictError("Mật khẩu mới không được trùng mật khẩu cũ")

        # ===== Update password =====
        try:
            user.password_hash = generate_password_hash(dto.new_password)
            user.failed_login_attempts = 0
            user.locked_until = None
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise