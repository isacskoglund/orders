from dataclasses import dataclass
from domain.models.identifier import Identifier
from domain.models.order import VersionedOrder
from domain.models.product import Product, ProductVersion


class DomainError(Exception):
    pass


# Id errors:


@dataclass(frozen=True)
class InvalidProductIdError(DomainError):
    """
    Could not find a product with the given id.
    """

    product_id: Identifier


@dataclass(frozen=True)
class InvalidProductVersionIdError(DomainError):
    """
    Could not find product version with the given id.
    """


@dataclass
class InvalidOrderIdError(DomainError):
    """
    Could not find an order with the given id.
    """

    order_id: Identifier


# Logical errors:


@dataclass(frozen=True)
class NoCurrentProductVersionError(DomainError):
    """
    The product with the given id has not current product version.
    """

    product_id: Identifier


@dataclass(frozen=True)
class InsufficientExpectednessError(DomainError):
    """
    The expectedness of the status update is insufficient.
    """


# Dependency errors:

# All dependencies should log/report errors individually.
# Below errors should be raised to allow for proper exception handling by caller.


@dataclass(frozen=True)
class SaveOrderError(DomainError):
    """
    The order could not be saved.
    """

    order: VersionedOrder


@dataclass(frozen=True)
class UpdateOrderError(DomainError):
    """
    Could not update order with id `order_id`.
    """

    order_id: Identifier


@dataclass(frozen=True)
class ReadFromPersistenceError(DomainError):
    """
    Could not read from persistence.
    """


@dataclass(frozen=True)
class AddProductError(DomainError):
    """
    Could not add the product to the product catalogue.
    """

    product: Product


@dataclass(frozen=True)
class AddProductVersionError(DomainError):
    """
    Could not add the product version to the product catalogue.
    """

    product_version: ProductVersion


@dataclass(frozen=True)
class SetCurrentProductVersionIdError(DomainError):
    """
    Could not set the current product version id
    of the product with id `product_id`.
    """

    product_id: Identifier
    product_version_id: Identifier
