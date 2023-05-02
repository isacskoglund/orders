from decimal import Decimal
from dataclasses import dataclass
from .identifiers import ProductId, ProductVersionId


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

    id: ProductVersionId
    product_id: ProductId
    price: Price
    data: Data


@dataclass(frozen=True)
class Product:
    id: ProductId
    current_version_id: ProductVersionId | None = None
