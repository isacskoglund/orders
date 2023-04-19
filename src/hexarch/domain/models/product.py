from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from identifiers import ProductId, ProductVersionId


@dataclass(frozen=True)
class Price:
    amount: Decimal
    unit: str
    currency: str


@dataclass(frozen=True)
class Description:
    pass


@dataclass(frozen=True)
class Name:
    pass


@dataclass(frozen=True)
class ProductVersion:
    id: ProductVersionId
    product_id: ProductId
    name: Name
    description: Description
    price: Price


@dataclass(frozen=True)
class Product:
    id: ProductId
    current_version: Optional[ProductVersion] = None
