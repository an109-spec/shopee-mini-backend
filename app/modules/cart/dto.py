from dataclasses import dataclass

@dataclass
class AddToCartDTO:
    product_id: int
    quantity: int


@dataclass
class UpdateCartItemDTO:
    product_id: int
    quantity: int