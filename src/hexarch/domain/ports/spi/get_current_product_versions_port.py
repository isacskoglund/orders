from typing import Protocol
from models.identifiers import ProductId, ProductVersionId


class GetCurrentProductVersionsPort(Protocol):
    def get_current_product_versions(
        self, product_ids: list[ProductId]
    ) -> dict[ProductId, ProductVersionId]:
        """
        Raises:
            InvalidProductIdError: Product was not found.
            NoCurrentProductVersionError: Product has no current version.
        """
        pass
