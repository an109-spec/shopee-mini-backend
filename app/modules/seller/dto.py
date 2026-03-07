from dataclasses import dataclass


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