from datetime import datetime, timezone
from app.extensions.db import db
from flask import jsonify
from app.models.promotion import Promotion
from app.models.flash_sale import FlashSale
from app.models.voucher import Voucher
from app.models.product import ProductVariant

class PromotionService:

    @staticmethod
    def create_promotion(name, variant_id, discount_percent, start_time, end_time):

        variant = ProductVariant.query.get(variant_id)

        if not variant:
            raise Exception("Variant không tồn tại")

        # ===== VALIDATE DISCOUNT =====
        if discount_percent <= 0 or discount_percent > 90:
            raise Exception("Discount không hợp lệ")

        # ===== VALIDATE TIME =====
        if start_time >= end_time:
            raise Exception("Thời gian khuyến mãi không hợp lệ")

        promo = Promotion(
            name=name,
            variant_id=variant_id,
            discount_percent=discount_percent,
            start_time=start_time,
            end_time=end_time,
        )

        db.session.add(promo)
        db.session.commit()

        return promo

    @staticmethod
    def delete_promotion(promo_id):

        promo = Promotion.query.get(promo_id)

        if not promo:
            return

        db.session.delete(promo)
        db.session.commit()

    @staticmethod
    def list_promotions(shop_id):

        from app.models.product import Product

        return (
            Promotion.query
            .join(ProductVariant, Promotion.variant_id == ProductVariant.id)
            .join(Product, ProductVariant.product_id == Product.id)
            .filter(Product.shop_id == shop_id)
            .all()
        )
    @staticmethod
    def get_active_promotions():

        now = datetime.now(timezone.utc)

        return Promotion.query.filter(
            Promotion.start_time <= now,
            Promotion.end_time >= now,
            Promotion.is_active == True
        ).all()
    @staticmethod
    def get_promotion(promo_id):

        promo = Promotion.query.get(promo_id)

        if not promo:
            raise Exception("Promotion không tồn tại")

        return promo
    @staticmethod
    def update_promotion(promo_id, name, discount_percent, start_time, end_time):

        promo = Promotion.query.get(promo_id)

        if not promo:
            raise Exception("Promotion không tồn tại")

        # ===== VALIDATE =====
        if discount_percent <= 0 or discount_percent > 90:
            raise Exception("Discount không hợp lệ")

        if start_time >= end_time:
            raise Exception("Thời gian không hợp lệ")

        promo.name = name
        promo.discount_percent = discount_percent
        promo.start_time = start_time
        promo.end_time = end_time

        db.session.commit()

        return promo
class VoucherService:

    @staticmethod
    def use_voucher(voucher):

        voucher.used_quantity += 1

        db.session.commit()
    @staticmethod
    def create_voucher(
        code,
        discount_type,
        discount_value,
        quantity,
        min_order,
        expired_at
    ):

        voucher = Voucher(
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            quantity=quantity,
            min_order_amount=min_order,
            expired_at=expired_at,
        )

        db.session.add(voucher)
        db.session.commit()

        return voucher


    @staticmethod
    def list_vouchers():

        return Voucher.query.order_by(
            Voucher.created_at.desc()
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

        if voucher.expired_at < datetime.now(timezone.utc):
            return None

        return voucher
class FlashSaleService:
    @staticmethod
    def increase_sold(variant_id, quantity):
        from app.utils.time import utcnow
        now=utcnow()
        sale = FlashSale.query.filter(
        FlashSale.variant_id == variant_id,
        FlashSale.is_active == True,
        FlashSale.start_time <= now,
        FlashSale.end_time >= now
        ).first()

        if not sale:
            return
        # kiểm tra stock flash sale
        if sale.sold_count + quantity > sale.stock_limit:
            raise Exception("Flash sale sold out")


        sale.sold_count += quantity

        db.session.commit()
    # =========================
    # FLASH SALE
    # =========================
    @staticmethod
    def create_flash_sale(
        variant_id,
        discount_percent,
        stock_limit,
        start_time,
        end_time
    ):
        variant_id = int(variant_id)
        discount_percent = int(discount_percent)
        stock_limit = int(stock_limit)
        # 1. kiểm tra variant tồn tại
        variant = ProductVariant.query.get(variant_id)
        print("variant_id:", variant_id)
        print("variant.stock:", variant.stock)
        print("stock_limit:", stock_limit)
        if not variant:
            raise Exception("Variant không tồn tại")
        if stock_limit <= 0 or stock_limit > variant.stock:
                raise Exception("Flash sale stock vượt tồn kho sản phẩm")
        

        # 2. kiểm tra thời gian
        now = datetime.now(timezone.utc)

        if start_time >= end_time:
            raise Exception("Thời gian khuyến mãi không hợp lệ")

        if end_time <= now:
            raise Exception("Thời gian kết thúc phải lớn hơn hiện tại")

        # 3. kiểm tra discount hợp lệ
        if discount_percent <= 0 or discount_percent > 90:
            raise Exception("Discount percent không hợp lệ")

        # 4. kiểm tra flash sale trùng
        exist = FlashSale.query.filter(
            FlashSale.variant_id == variant_id,
            FlashSale.end_time >= start_time,
            FlashSale.start_time <= end_time
        ).first()

        if exist:
            raise Exception("Variant đã có flash sale trong khoảng thời gian này")

        # 5. tạo flash sale
        sale = FlashSale(
            variant_id=variant_id,
            discount_percent=discount_percent,
            stock_limit=stock_limit,
            sold_count=0,
            start_time=start_time,
            end_time=end_time,
            is_active=True
        )

        db.session.add(sale)
        db.session.commit()

        return sale


    @staticmethod
    def list_flash_sales(shop_id):

        return (
            FlashSale.query
            .join(ProductVariant)
            .join(ProductVariant.product)
            .filter_by(shop_id=shop_id)
            .all()
        )
    @staticmethod
    def get_active_flash_sales():

        return FlashSale.query.filter(
            FlashSale.is_active == True,
            FlashSale.start_time <= datetime.now(timezone.utc),
            FlashSale.end_time >= datetime.now(timezone.utc)
        ).all()