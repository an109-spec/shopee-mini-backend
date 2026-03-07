from app.models import Order, OrderItem, Product


class OrderManager:

    @staticmethod
    def get_orders(shop_id):

        return (
            Order.query
            .join(OrderItem, OrderItem.order_id == Order.id)
            .join(Product, Product.id == OrderItem.product_id)
            .filter(Product.shop_id == shop_id)
            .distinct()
            .all()
        )