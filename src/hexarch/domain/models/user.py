from enum import Enum
from dataclasses import dataclass
from identifiers import UserId, CustomerId
from order import Order, Address
from product import Product


@dataclass(frozen=True)
class User:
    id: UserId


@dataclass(frozen=True)
class Customer(User):
    id: CustomerId
