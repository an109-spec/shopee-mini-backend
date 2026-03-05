from app.extensions.db import db
from app.models.order import Order
from app.modules.audit.service import AuditService


class OrderManager:

    @staticmethod
    def list_orders():

        return Order.query.order_by(
            Order.created_at.desc()
        ).all()


    @staticmethod
    def change_status(order_id, status, admin_id):

        order = Order.query.get_or_404(order_id)

        order.status = status

        db.session.commit()

        AuditService.log(
            user_id=admin_id,
            action="change_order_status",
            target=f"order:{order_id}"
        )

        return order