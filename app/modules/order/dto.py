from dataclasses import dataclass
from .status import PaymentMethod, OrderStatus


@dataclass
class CreateOrderDTO:
    user_id: int
    payment_method: PaymentMethod


@dataclass
class UpdateStatusDTO:
    order_id: int
    new_status: OrderStatus