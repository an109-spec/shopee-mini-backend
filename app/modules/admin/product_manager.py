from app.extensions.db import db
from app.models.product import Product
from app.modules.audit.service import AuditService


class ProductManager:

    @staticmethod
    def list_products():

        return Product.query.all()


    @staticmethod
    def update_price(product_id, new_price, admin_id):

        product = Product.query.get_or_404(product_id)

        old_price = product.price

        product.price = new_price

        db.session.commit()

        AuditService.log(
            user_id=admin_id,
            action="admin_update_price",
            target=f"product:{product_id}"
        )

        return product