import logging
from app.common.exceptions import ValidationError

logger = logging.getLogger(__name__)


class SMSService:
    """
    Service gửi SMS (OTP, 2FA).
    Có thể thay bằng Twilio/Viettel/Vonage sau này.
    """

    @staticmethod
    def send(phone: str, message: str) -> None:
        if not phone or not phone.strip():
            raise ValidationError("Số điện thoại không hợp lệ")

        phone = phone.strip()

        try:
            # ===== DEVELOPMENT MODE =====
            # TODO: thay bằng provider thật
            logger.info(f"[DEV SMS] To: {phone} | Message: {message}")

            # ===== PRODUCTION MODE =====
            # Ví dụ tích hợp Twilio:
            # client.messages.create(
            #     body=message,
            #     from_=TWILIO_PHONE,
            #     to=phone
            # )

        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            raise