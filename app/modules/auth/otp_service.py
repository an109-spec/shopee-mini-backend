from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.otp import OTPCode
from app.common.security.otp import (
    generate_otp,
    get_otp_expired_at,
    is_otp_expired,
)


class OTPService:

    @staticmethod
    def create_otp(user_id: int, otp_type: str = "email") -> str:
        """
        Tạo OTP mới, xoá OTP chưa dùng trước đó
        """

        # Xoá OTP cũ chưa dùng
        OTPCode.query.filter(
            and_(
                OTPCode.user_id == user_id,
                OTPCode.type == otp_type,
                OTPCode.is_used.is_(False),
            )
        ).delete(synchronize_session=False)

        raw_code = generate_otp()

        otp = OTPCode(
            user_id=user_id,
            otp_code=generate_password_hash(raw_code),  # HASH OTP
            type=otp_type,
            expired_at=get_otp_expired_at(),
            is_used=False,
            failed_attempts=0,
        )

        db.session.add(otp)
        db.session.commit()

        return raw_code

    @staticmethod
    def verify_otp(user_id: int, code: str, otp_type: str = "email") -> bool:
        """
        Verify OTP an toàn
        """

        otp = OTPCode.query.filter_by(
            user_id=user_id,
            type=otp_type,
            is_used=False,
        ).order_by(OTPCode.created_at.desc()).first()

        if not otp:
            return False

        # Hết hạn
        if is_otp_expired(otp.expired_at):
            return False

        # So sánh hash
        if not check_password_hash(otp.otp_code, code):
            otp.failed_attempts += 1

            # Giới hạn brute force (ví dụ 5 lần)
            if otp.failed_attempts >= 5:
                otp.is_used = True

            db.session.commit()
            return False

        # OTP đúng
        otp.is_used = True
        db.session.commit()

        return True