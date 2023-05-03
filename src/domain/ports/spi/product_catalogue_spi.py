from typing import Protocol
from domain.models.identifier import Identifier
from domain.models.product import Product, ProductVersion


class ProductCatalogueSPI(Protocol):
    def validate_product_id(self, product_id: Identifier) -> bool:
        pass

    def get_product(self, product_id: Identifier) -> Product | None:
        pass

    def get_product_version(
        self, product_version_id: Identifier
    ) -> ProductVersion | None:
        pass
