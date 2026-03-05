from app.models.flash_sale import FlashSale
from app.extensions.db import db


class FlashSaleService:

    @staticmethod
    def increase_sold(product_id, quantity):

        sale = FlashSale.query.filter_by(
            product_id=product_id,
            is_active=True
        ).first()

        if not sale:
            return

        sale.sold_count += quantity

        db.session.commit()