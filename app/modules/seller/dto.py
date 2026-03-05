from dataclasses import dataclass


@dataclass
class CreateShopDTO:
    name: str


@dataclass
class CreateProductDTO:
    name: str
    price: float
    stock: int
    description: str | None = None