from app.extensions import db
from app.models import Shop, Product, User


class SellerService:

    @staticmethod
    def register_shop(user: User, name: str):

        shop = Shop(
            owner_id=user.id,
            name=name
        )

        user.role = "seller"

        db.session.add(shop)
        db.session.commit()

        return shop