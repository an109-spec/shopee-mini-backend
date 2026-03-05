from app.models import Order


class OrderManager:

    @staticmethod
    def get_orders(shop_id):

        return (
            Order.query
            .join(Order.items)
            .filter_by(shop_id=shop_id)
            .all()
        )