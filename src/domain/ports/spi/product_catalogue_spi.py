from typing import Protocol
from domain.models.identifier import Identifier
from domain.models.product import Product, ProductVersion
from dataclasses import dataclass


class ValidateProductIdSPI(Protocol):
    @dataclass
    class Result:
        valid_ids: set[Identifier]
        invalid_ids: set[Identifier]

    def validate_product_ids(self, product_ids: list[Identifier]) -> Result:
        ...


class GetProductSPI(Protocol):
    @dataclass
    class Result:
        products: dict[Identifier, Product]
        invalid_ids: set[Identifier]

    def get_product(self, product_ids: list[Identifier]) -> Result:
        ...


class GetProductVersionIdsSPI(Protocol):
    @dataclass
    class Result:
        product_version_ids: dict[Identifier, Identifier]
        invalid_ids: set[Identifier]
        ids_without_product_version_id: set[
            Identifier
        ]  # Contains each valid id in product_ids that
        # have no product_version_id currently assigned to its product.

    def get_product_versions(self, product_ids: list[Identifier]) -> Result:
        ...


class GetProductVersionsSPI(Protocol):
    @dataclass
    class Result:
        product_versions: dict[Identifier, ProductVersion]
        invalid_ids: set[Identifier]
        ids_without_product_version_id: set[
            Identifier
        ]  # Contains each valid id in product_ids that
        # have no product_version currently assigned to its product.

    def get_product_versions(self, product_ids: list[Identifier]) -> Result:
        ...


class AddProductsSPI(Protocol):
    def add_products(self, products: list[Product]) -> None:
        """
        Raises:
            AddProductError
        """


class AddProductVersionsSPI(Protocol):
    def add_product_versions(self, product_versions: list[ProductVersion]) -> None:
        """
        Raises:
            AddProductVersionError
        """


class SetCurrentProductVersionIdSPI(Protocol):
    def set_current_product_version(
        self, current_product_versions: dict[Identifier, Identifier | None]
    ) -> None:
        """
        Args:
            current_product_versions (dict): Keys are product_ids,
                values are product_version_ids or None.
                Maps each product_id to a single product_version_id or None.
                None signifies that the product has no current product version.

        Raises:
            InvalidProductIdError
            InvalidProductVersionIdError
            SetCurrentProductVersionIdError
        """
        ...
