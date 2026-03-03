import logging
import re
from flask import current_app
from app.common.exceptions import ValidationError

logger = logging.getLogger(__name__)


class SMSService:

    PHONE_REGEX = r"^\+?\d{9,15}$"

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        phone = phone.strip().replace(" ", "").replace("-", "")

        # Chuẩn hóa VN
        if phone.startswith("0"):
            phone = "+84" + phone[1:]

        return phone

    @staticmethod
    def send(phone: str, message: str) -> None:
        if not phone:
            raise ValidationError("Số điện thoại không hợp lệ")

        if not message:
            raise ValidationError("Nội dung SMS không hợp lệ")

        phone = SMSService._normalize_phone(phone)

        if not re.match(SMSService.PHONE_REGEX, phone):
            raise ValidationError("Số điện thoại không hợp lệ")

        try:
            # ===== DEVELOPMENT =====
            if current_app.debug:
                logger.info(f"[DEV SMS] To: {phone} | Message: {message}")
                return

            # ===== PRODUCTION =====
            # TODO: tích hợp provider thật
            logger.info(f"[PROD SMS] Sending to {phone}")

        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            raise RuntimeError("Không thể gửi SMS")