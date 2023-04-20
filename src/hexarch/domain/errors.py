from dataclasses import dataclass
from models.identifiers import ProductId, OrderId


class DomainError(Exception):
    pass


# InvalidIdError:


class InvalidIdError(Exception):
    pass


@dataclass(frozen=True)
class InvalidProductIdError(InvalidIdError):
    product_id: ProductId


@dataclass(frozen=True)
class InvalidOrderIdError(InvalidIdError):
    order_id: OrderId


# NoCurrentProductVersionError:


@dataclass(frozen=True)
class NoCurrentProductVersionError(DomainError):
    product_id: ProductId
