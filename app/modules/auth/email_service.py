import logging

from flask_mail import Message

from app.extensions import mail

logger = logging.getLogger(__name__)


class EmailService:
    """Service gửi email (OTP, thông báo bảo mật...)."""

    @staticmethod
    def send_otp(email: str, otp_code: str) -> None:
        if not email or not email.strip():
            raise ValueError("Email không hợp lệ")

        email = email.strip()

        subject = "Mã OTP đặt lại mật khẩu"
        body = (
            "Xin chào,\n\n"
            "Bạn vừa yêu cầu đặt lại mật khẩu cho tài khoản Shopee Mini.\n"
            f"Mã OTP của bạn là: {otp_code}\n"
            "Mã có hiệu lực trong 5 phút.\n\n"
            "Nếu bạn không thực hiện yêu cầu này, vui lòng bỏ qua email."
        )

        message = Message(
            subject=subject,
            recipients=[email],
            body=body,
        )

        mail.send(message)
        logger.info("OTP email sent to %s", email)