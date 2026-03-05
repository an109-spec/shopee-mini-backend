import uuid
from decimal import Decimal
from flask import session
from app.extensions.db import db
from app.models import Order, OrderItem, Product
from app.common.exceptions import (
    NotFoundError,
    ValidationError,
    ForbiddenError,
)
from .status import OrderStatus
from .workflow import apply_transition


class OrderService:

    SESSION_KEY = "cart"

    @staticmethod
    def _generate_order_code():
        return uuid.uuid4().hex[:12].upper()

    @staticmethod
    def create_order_from_cart(user_id, payment_method):

        cart = session.get(OrderService.SESSION_KEY)

        if not cart or not cart.get("items"):
            raise ValidationError("Giỏ hàng trống")

        items = cart["items"]

        order = Order(
            user_id=user_id,
            total_price=Decimal("0"),
            status=OrderStatus.PENDING,
            payment_method=payment_method,
            order_code=OrderService._generate_order_code()
        )

        db.session.add(order)
        db.session.flush()

        total = Decimal("0")

        for item in items.values():
            product = Product.query.get(item["product_id"])

            if not product:
                raise NotFoundError("Sản phẩm không tồn tại")

            quantity = int(item["quantity"])

            if product.stock_quantity < quantity:
                raise ValidationError("Không đủ tồn kho")

            subtotal = product.price * quantity
            total += subtotal

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                price=product.price,
                quantity=quantity,
                subtotal=subtotal
            )

            product.stock_quantity -= quantity
            db.session.add(order_item)

        order.total_price = total
        db.session.commit()

        apply_transition(order, OrderStatus.CONFIRMED)

        session.pop(OrderService.SESSION_KEY, None)

        return order

    @staticmethod
    def cancel_order(order_id, user_id):
        order = db.session.get(Order, order_id)

        if not order:
            raise NotFoundError("Không tìm thấy đơn hàng")

        if order.user_id != user_id:
            raise ForbiddenError("Không có quyền huỷ đơn")

        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise ValidationError("Không thể huỷ đơn ở trạng thái này")

        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock_quantity += item.quantity

        apply_transition(order, OrderStatus.CANCELLED)

    @staticmethod
    def get_user_orders(user_id):

        orders = (
            Order.query
            .filter_by(user_id=user_id)
            .order_by(Order.created_at.desc())
            .all()
        )

        return orders

    @staticmethod
    def get_order_detail(order_id, user_id):

        order = db.session.get(Order, order_id)

        if not order:
            raise NotFoundError("Không tìm thấy đơn hàng")

        if order.user_id != user_id:
            raise ForbiddenError("Không có quyền xem đơn này")

        return order

    @staticmethod
    def update_status(order_id, new_status):
        order = db.session.get(Order, order_id)

        if not order:
            raise NotFoundError("Không tìm thấy đơn hàng")

        apply_transition(order, new_status)
        db.session.commit()
    @staticmethod
    def get_all_orders():
        return (
            Order.query
            .order_by(Order.created_at.desc())
            .all()
        )

    @staticmethod
    def get_order_detail_admin(order_id):
        order = db.session.get(Order, order_id)

        if not order:
            raise NotFoundError("Không tìm thấy đơn hàng")

        return order

    @staticmethod
    def track_by_order_code(order_code):
        order = (
            Order.query
            .filter_by(order_code=order_code)
            .first()
        )

        if not order:
            raise NotFoundError("Không tìm thấy đơn hàng")

        return order

    @staticmethod
    def build_timeline(order):
        """
        Trả về list timeline trạng thái để render UI
        """
        timeline = []

        steps = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.SHIPPING,
            OrderStatus.COMPLETED,
            OrderStatus.CANCELLED
        ]

        for step in steps:
            timeline.append({
                "status": step,
                "is_active": order.status == step
            })

        return timeline