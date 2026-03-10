from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal


@dataclass
class SellerProductCreateDTO:

    name: str
    description: Optional[str]
    price: Decimal
    stock: int
    category_id: Optional[int]
    images: List[str]

@dataclass
class CreateShopDTO:
    name: str
    pickup_address: str
    email: str
    phone: str


@dataclass
class ShippingSetupDTO:
    fast: bool
    same_day: bool
    express: bool
    self_delivery: bool
    pickup_point: bool
    bulky: bool

@dataclass
class CreateProductDTO:
    name: str
    price: float
    stock: int
    description: str | None = None
