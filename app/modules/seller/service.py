from app.extensions import db
from app.models import Shop, User
from app.common.exceptions import ValidationError


class SellerService:

    @staticmethod
    def register_shop(user, name):

        shop = Shop(
            owner_id=user.id,
            name=name
        )

        db.session.add(shop)

        # QUAN TRỌNG
        if user.role != "seller":
            user.role = "seller"

        db.session.commit()

        return shop


    @staticmethod
    def setup_shipping(shop: Shop, data):

        shop.shipping_fast = data.get("fast") == "on"
        shop.shipping_same_day = data.get("same_day") == "on"
        shop.shipping_express = data.get("express") == "on"
        shop.shipping_self_delivery = data.get("self_delivery") == "on"
        shop.shipping_bulky = data.get("bulky") == "on"

        shop.shipping_configured = True

        db.session.commit()

        return shop