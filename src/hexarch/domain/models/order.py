from __future__ import annotations
from identifiers import OrderId
from identifiers import CustomerId
from enum import Enum
from dataclasses import dataclass, replace
from product import ProductVersion


class OrderStatus(Enum):
    PENDING = "pending"
    PAYMENT_COMPLETE = "payment_complete"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Address:
    street: str
    city: str
    postal_code: str
    country: str


@dataclass(frozen=True)
class OrderItem:
    product_version: ProductVersion
    quantity: int


@dataclass(frozen=True)
class Order:
    id: OrderId
    customer_id: CustomerId
    address: Address
    items: list[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
