from dataclasses import dataclass
from typing import Optional


@dataclass
class CreatePaymentDTO:
    order_id: int
    method: str


@dataclass
class ConfirmPaymentDTO:
    order_id: int
    transaction_code: Optional[str] = None