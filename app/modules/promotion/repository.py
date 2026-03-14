from datetime import datetime
from app.extensions import db

from app.models.promotion import Promotion
from app.models.flash_sale import FlashSale
from app.models.voucher import Voucher
from app.models.product import ProductVariant, Product


# =========================
# PROMOTION
# =========================
class PromotionRepository:

    @staticmethod
    def list_promotions_for_shop(shop_id):
        return (
            db.session.query(Promotion)
            .join(ProductVariant, ProductVariant.id == Promotion.variant_id)
            .join(Product, Product.id == ProductVariant.product_id)
            .filter(Product.shop_id == shop_id)
            .order_by(Promotion.start_time.desc())
            .all()
        )

    @staticmethod
    def create_promotion(promo: Promotion):
        db.session.add(promo)
        db.session.flush()
        return promo

    @staticmethod
    def delete_promotion(promo_id):
        promo = db.session.get(Promotion, promo_id)

        if promo:
            db.session.delete(promo)


# =========================
# FLASH SALE
# =========================
class FlashSaleRepository:

    @staticmethod
    def create_flash_sale(
        variant_id: int,
        discount_percent: int,
        stock_limit: int,
        start_time: datetime,
        end_time: datetime
    ):

        flash_sale = FlashSale(
            variant_id=variant_id,
            discount_percent=discount_percent,
            stock_limit=stock_limit,
            start_time=start_time,
            end_time=end_time,
            is_active=True,
        )

        db.session.add(flash_sale)
        db.session.flush()

        return flash_sale

    @staticmethod
    def list_flash_sales_for_shop(shop_id: int):

        return (
            db.session.query(FlashSale)
            .join(ProductVariant, ProductVariant.id == FlashSale.variant_id)
            .join(Product, Product.id == ProductVariant.product_id)
            .filter(Product.shop_id == shop_id)
            .order_by(FlashSale.start_time.desc())
            .all()
        )

    @staticmethod
    def delete_flash_sale(flash_id):

        flash = db.session.get(FlashSale, flash_id)

        if flash:
            db.session.delete(flash)


# =========================
# VOUCHER
# =========================
class VoucherRepository:

    @staticmethod
    def create_voucher(
        shop_id: int,
        name: str,
        code: str,
        discount_type: str,
        discount_value: int,
        min_order_value: int,
        usage_limit: int,
        start_time: datetime,
        end_time: datetime
    ):

        voucher = Voucher(
            shop_id=shop_id,
            name=name,
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            min_order_value=min_order_value,
            usage_limit=usage_limit,
            used_count=0,
            start_time=start_time,
            end_time=end_time,
            is_active=True
        )

        db.session.add(voucher)
        db.session.flush()

        return voucher

    @staticmethod
    def list_vouchers_for_shop(shop_id):

        return (
            db.session.query(Voucher)
            .filter(Voucher.shop_id == shop_id)
            .order_by(Voucher.start_time.desc())
            .all()
        )

    @staticmethod
    def delete_voucher(voucher_id):

        voucher = db.session.get(Voucher, voucher_id)

        if voucher:
            db.session.delete(voucher)


# =========================
# COMMIT
# =========================
class RepositoryCommit:

    @staticmethod
    def commit():
        db.session.commit()