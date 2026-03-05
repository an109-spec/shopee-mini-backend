from decimal import Decimal
from typing import Dict


def calculate_subtotal(items: Dict) -> Decimal:
    subtotal = Decimal("0")
    for item in items.values():
        price = Decimal(item["price"])
        qty = int(item["quantity"])
        subtotal += price * qty
    return subtotal


def calculate_discount(subtotal: Decimal) -> Decimal:
    # Tạm thời chưa có discount
    return Decimal("0")


def calculate_total(subtotal: Decimal, discount: Decimal) -> Decimal:
    return subtotal - discount