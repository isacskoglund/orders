from decimal import Decimal
from dataclasses import dataclass
from .identifier import Identifier


@dataclass(frozen=True)
class ProductVersion:
    @dataclass(frozen=True)
    class Price:
        amount: Decimal
        unit: str
        currency: str

    @dataclass(frozen=True)
    class Data:
        pass

    id: Identifier
    product_id: Identifier
    price: Price
    data: Data


@dataclass(frozen=True)
class Product:
    id: Identifier
    current_version_id: Identifier | None = None
