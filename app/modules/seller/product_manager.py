from app.extensions import db
from app.models import Product
from app.core.enums.product_status import ProductStatus
from .dto import CreateProductDTO


class ProductManager:

    @staticmethod
    def create(shop_id: int, dto: CreateProductDTO):

        product = Product(
            shop_id=shop_id,
            name=dto.name,
            slug=f"{dto.name.strip().lower().replace(' ', '-')}-{shop_id}",
            price=dto.price,
            stock_quantity=dto.stock,
            description=dto.description,
            status=ProductStatus.ACTIVE,
        )

        db.session.add(product)
        db.session.commit()

        return product

    @staticmethod
    def get_products(shop_id: int):

        return Product.query.filter(
            Product.shop_id == shop_id,
            Product.status != ProductStatus.DELETED,
        ).all()

    @staticmethod
    def delete(product_id: int):

        product = Product.query.get(product_id)

        if not product:
            return

        product.status = ProductStatus.DELETED
        db.session.commit()