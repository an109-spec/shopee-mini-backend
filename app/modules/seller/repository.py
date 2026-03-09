from datetime import datetime
from sqlalchemy import func
from app.extensions import db
from app.models import Product, ProductImage, Shop, Order, OrderItem, FlashSale, ChatRoom, Message
from app.core.enums.order_status import OrderStatus
from app.core.enums.product_status import ProductStatus
from app.models.product import ProductVariant, VariantAttribute

class SellerRepository:

    @staticmethod
    def get_shop_by_owner_id(owner_id: int):
        return Shop.query.filter_by(owner_id=owner_id).first()

    @staticmethod
    def get_shop_by_id(shop_id: int):
        return db.session.get(Shop, shop_id)

    @staticmethod
    def create_product(product: Product):
        db.session.add(product)
        db.session.flush()
        return product

    @staticmethod
    def create_product_images(product_id: int, image_urls: list[str]):
        images = [ProductImage(product_id=product_id, image_url=url) for url in image_urls]
        db.session.add_all(images)

    @staticmethod
    def list_products(shop_id: int):
        return (
            Product.query
            .filter(
                Product.shop_id == shop_id,
                Product.status != ProductStatus.DELETED,
            )
            .order_by(Product.created_at.desc())
            .all()
        )

    @staticmethod
    def get_product(shop_id, product_id):
        from app.models import Product

        return Product.query.filter_by(
            id=product_id,
            shop_id=shop_id
        ).first()

    @staticmethod
    def get_orders_by_shop(shop_id: int, status: OrderStatus | None = None):

        query = (
            Order.query
            .join(OrderItem, OrderItem.order_id == Order.id)
            .join(Product, Product.id == OrderItem.product_id)
            .filter(Product.shop_id == shop_id)
            .distinct()
            .order_by(Order.created_at.desc())
        )

        if status:
            query = query.filter(Order.status == status)

        return query.all()

    @staticmethod
    def get_order_by_shop(order_id: int, shop_id: int):
        return (
            Order.query
            .join(OrderItem, OrderItem.order_id == Order.id)
            .join(Product, Product.id == OrderItem.product_id)
            .filter(
                Order.id == order_id,
                Product.shop_id == shop_id
            )
            .first()
        )

    @staticmethod
    def list_chat_rooms_for_seller(seller_id: int):
        return (
            ChatRoom.query
            .filter_by(seller_id=seller_id)
            .order_by(ChatRoom.created_at.desc())
            .all()
        )

    @staticmethod
    def list_messages(room_id: int, limit: int = 50):
        return (
            Message.query
            .filter_by(room_id=room_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def create_flash_sale(product_id: int, discount_price, start_time: datetime, end_time: datetime):

        flash_sale = FlashSale(
            product_id=product_id,
            discount_price=discount_price,
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
            FlashSale.query
            .join(Product, Product.id == FlashSale.product_id)
            .filter(Product.shop_id == shop_id)
            .order_by(FlashSale.created_at.desc())
            .all()
        )

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def get_shop_revenue(shop_id: int):

        revenue = (
            db.session.query(func.sum(OrderItem.price * OrderItem.quantity))
            .join(Product, Product.id == OrderItem.product_id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(
                Product.shop_id == shop_id,
                Order.status == OrderStatus.DELIVERED
            )
            .scalar()
        )

        return revenue or 0
    @staticmethod
    def create_product_variants(product_id, variants):

        for v in variants:

            variant = ProductVariant(
                product_id=product_id,
                price=v["price"],
                stock=v["stock"]
            )

            db.session.add(variant)
            db.session.flush()

            for name, value in v["attributes"].items():

                attr = VariantAttribute(
                    variant_id=variant.id,
                    name=name,
                    value=value
                )

                db.session.add(attr)
    @staticmethod
    def delete_variants(product_id):

        variants = ProductVariant.query.filter_by(
            product_id=product_id
        ).all()

        for v in variants:
            db.session.delete(v)