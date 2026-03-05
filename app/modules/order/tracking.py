from app.models import Order
from app.common.exceptions import NotFoundError
from .workflow import build_timeline


def track_by_order_code(order_code: str):

    order = Order.query.filter_by(order_code=order_code).first()

    if not order:
        raise NotFoundError("Không tìm thấy đơn hàng")

    return {
        "order_code": order.order_code,
        "status": order.status,
        "timeline": build_timeline(order)
    }