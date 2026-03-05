from datetime import datetime
from app.extensions.db import db
from app.models import Payment, Order
from app.common.exceptions import NotFoundError
from app.core.enums.order_status import OrderStatus
from .gateway import generate_qr_payment


class PaymentService:

    @staticmethod
    def create_payment(order):

        payment = Payment(
            order_id=order.id,
            method=order.payment_method,
            status="PENDING",
            amount=order.total_price,
            provider="MOCK"
        )

        db.session.add(payment)
        db.session.commit()

        if order.payment_method == "VNPAY":

            qr = generate_qr_payment(order)

            payment.transaction_code = qr["transaction_code"]

            db.session.commit()

            return qr

        return None

    @staticmethod
    def confirm_payment(order_id):

        order = db.session.get(Order, order_id)

        if not order:
            raise NotFoundError("Order not found")

        payment = Payment.query.filter_by(order_id=order_id).first()

        if not payment:
            raise NotFoundError("Payment not found")

        payment.status = "PAID"
        payment.paid_at = datetime.utcnow()

        order.status = OrderStatus.CONFIRMED

        db.session.commit()

        return True

    @staticmethod
    def handle_webhook(data):

        order_id = data.get("order_id")

        return PaymentService.confirm_payment(order_id)