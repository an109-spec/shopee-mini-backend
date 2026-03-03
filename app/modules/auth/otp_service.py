from datetime import datetime, timedelta, timezone

from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.otp import OTPCode
from app.common.security.otp import (
    generate_otp,
    get_otp_expired_at,
    is_otp_expired,
)
from app.common.exceptions import ValidationError, TooManyRequestsError
from .mail_service import MailService
from .sms_service import SMSService


class OTPService:

    MAX_FAILED_ATTEMPTS = 5
    RESEND_COOLDOWN_SECONDS = 60
    MAX_REQUESTS_PER_15_MIN = 3

    # ==========================================================
    # CREATE OTP
    # ==========================================================

    @staticmethod
    def create_otp(user, otp_type: str = "email") -> str:
        """
        Tạo OTP mới, có rate limit & resend cooldown
        """

        now = datetime.now(timezone.utc)

        # ===== Rate limit 15 phút =====
        fifteen_minutes_ago = now - timedelta(minutes=15)

        recent_count = OTPCode.query.filter(
            and_(
                OTPCode.user_id == user.id,
                OTPCode.type == otp_type,
                OTPCode.created_at >= fifteen_minutes_ago,
            )
        ).count()

        if recent_count >= OTPService.MAX_REQUESTS_PER_15_MIN:
            raise TooManyRequestsError("Bạn đã yêu cầu quá nhiều mã OTP. Vui lòng thử lại sau.")

        # ===== Cooldown resend =====
        latest_otp = OTPCode.query.filter(
            and_(
                OTPCode.user_id == user.id,
                OTPCode.type == otp_type,
                OTPCode.is_used.is_(False),
            )
        ).order_by(OTPCode.created_at.desc()).first()

        if latest_otp:
            diff = (now - latest_otp.created_at).total_seconds()
            if diff < OTPService.RESEND_COOLDOWN_SECONDS:
                raise ValidationError("Vui lòng chờ trước khi yêu cầu mã mới.")

            # Xoá OTP cũ chưa dùng
            db.session.delete(latest_otp)

        # ===== Generate OTP =====
        raw_code = generate_otp()

        otp = OTPCode(
            user_id=user.id,
            otp_code=generate_password_hash(raw_code),
            type=otp_type,
            expired_at=get_otp_expired_at(),
            is_used=False,
            failed_attempts=0,
        )

        db.session.add(otp)
        db.session.commit()

        # ===== SEND OTP =====
        if otp_type == "email" and user.email:
            MailService.send_otp_email(user.email, raw_code)

        elif otp_type == "sms" and user.phone:
            SMSService.send(user.phone, f"Mã OTP của bạn là {raw_code}")

        return raw_code

    # ==========================================================
    # VERIFY OTP
    # ==========================================================

    @staticmethod
    def verify_otp(user_id: int, code: str, otp_type: str = "email") -> bool:
        """
        Verify OTP an toàn, chống brute force
        """

        otp = OTPCode.query.filter_by(
            user_id=user_id,
            type=otp_type,
            is_used=False,
        ).order_by(OTPCode.created_at.desc()).first()

        if not otp:
            return False

        # ===== Check expiration =====
        if is_otp_expired(otp.expired_at):
            otp.is_used = True
            db.session.commit()
            return False

        # ===== Check brute force limit =====
        if otp.failed_attempts >= OTPService.MAX_FAILED_ATTEMPTS:
            otp.is_used = True
            db.session.commit()
            return False

        # ===== Check hash =====
        if not check_password_hash(otp.otp_code, code):
            otp.failed_attempts += 1

            if otp.failed_attempts >= OTPService.MAX_FAILED_ATTEMPTS:
                otp.is_used = True

            db.session.commit()
            return False

        # ===== Success =====
        otp.is_used = True
        db.session.commit()
        return True