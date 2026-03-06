from app.extensions import db
from app.models import Shop, User


class SellerService:

    @staticmethod
    def register_shop(user: User, name: str):

        shop = Shop(
            owner_id=user.id,
            name=name
        )

        db.session.add(shop)
        db.session.commit()

        return shop