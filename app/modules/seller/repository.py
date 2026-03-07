from app.extensions import db
from app.models import Product, ProductImage, Shop, Order, OrderItem
from app.core.enums.order_status import OrderStatus
from app.core.enums.product_status import ProductStatus


class SellerRepository:
    @staticmethod
    def get_shop_by_owner_id(owner_id: int):
        return Shop.query.filter_by(owner_id=owner_id).first()

    @staticmethod
    def create_product(product: Product):
        db.session.add(product)
        db.session.flush()
        return product

    @staticmethod
    def create_product_images(product_id: int, image_urls: list[str]):
        for image_url in image_urls:
            db.session.add(ProductImage(product_id=product_id, image_url=image_url))

    @staticmethod
    def list_products(shop_id: int):
        return (
            Product.query.filter(
                Product.shop_id == shop_id,
                Product.status != ProductStatus.DELETED,
            )
            .order_by(Product.created_at.desc())
            .all()
        )

    @staticmethod
    def get_product(product_id: int):
        return Product.query.get(product_id)

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def get_orders_by_shop(shop_id: int, status: OrderStatus | None = None):
        query = (
            Order.query.join(OrderItem, OrderItem.order_id == Order.id)
            .join(Product, Product.id == OrderItem.product_id)
            .filter(Product.shop_id == shop_id)
            .distinct()
            .order_by(Order.created_at.desc())
        )
        if status:
            query = query.filter(Order.status == status)
        return query.all()