from sqlalchemy import func
from app.extensions.db import db
from app.models.order import Order
from app.models.user import User
from app.models.product import Product
from app.models.order import OrderItem


class DashboardService:

    @staticmethod
    def total_orders():

        return db.session.query(
            func.count(Order.id)
        ).scalar()


    @staticmethod
    def monthly_revenue():

        revenue = db.session.query(
            func.sum(Order.total_price)
        ).filter(
            Order.status == "COMPLETED"
        ).scalar()

        return revenue or 0


    @staticmethod
    def new_users():

        return db.session.query(
            func.count(User.id)
        ).filter(
            User.created_at >= func.now() - func.interval("30 day")
        ).scalar()


    @staticmethod
    def top_5_products():

        result = db.session.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label("sold")
        ).join(
            OrderItem.product_id == Product.id
        ).group_by(
            Product.id
        ).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(5).all()

        return result