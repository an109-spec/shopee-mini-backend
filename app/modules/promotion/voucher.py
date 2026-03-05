from app.models.voucher import Voucher
from app.extensions.db import db


class VoucherService:

    @staticmethod
    def use_voucher(voucher):

        voucher.used_quantity += 1

        db.session.commit()