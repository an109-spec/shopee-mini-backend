from enum import Enum


class ProductStatus(str, Enum):
    ACTIVE = "ACTIVE"
    HIDDEN = "HIDDEN"
    DELETED = "DELETED"