from app.models.flash_sale import FlashSale
from app.models.voucher import Voucher
from app.extensions.db import db
from datetime import datetime


class PromotionService:

    @staticmethod
    def get_active_flash_sales():

        return FlashSale.query.filter(
            FlashSale.is_active == True,
            FlashSale.start_time <= datetime.utcnow(),
            FlashSale.end_time >= datetime.utcnow()
        ).all()


    @staticmethod
    def validate_voucher(code):

        voucher = Voucher.query.filter_by(
            code=code
        ).first()

        if not voucher:
            return None

        if voucher.used_quantity >= voucher.quantity:
            return None

        if voucher.expired_at < datetime.utcnow():
            return None

        return voucher