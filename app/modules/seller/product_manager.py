from app.extensions import db
from app.models import Product


class ProductManager:

    @staticmethod
    def create(shop_id, dto):

        product = Product(
            shop_id=shop_id,
            name=dto.name,
            price=dto.price,
            stock=dto.stock,
            description=dto.description
        )

        db.session.add(product)
        db.session.commit()

        return product

    @staticmethod
    def get_products(shop_id):
        return Product.query.filter_by(shop_id=shop_id).all()

    @staticmethod
    def delete(product_id):
        product = Product.query.get(product_id)
        db.session.delete(product)
        db.session.commit()