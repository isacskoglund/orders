from typing import Protocol
from dataclasses import dataclass
from models.identifiers import ProductId
from models.product import ProductVersion


class GetCurrentProductVersionsByProductIdsPort(Protocol):
    # Results:
    @dataclass
    class GetCurrentProductVersionsByProductIdsResult:
        pass

    class ProductVersionsNotFoundResult(GetCurrentProductVersionsByProductIdsResult):
        product_ids_not_found: list[ProductId]

    class SuccessfullyFoundProductVersions(GetCurrentProductVersionsByProductIdsResult):
        product_versions: list[ProductVersion]

    # Port:
    def get_current_product_versions_by_product_ids(
        self, product_ids: ProductId
    ) -> GetCurrentProductVersionsByProductIdsResult:
        raise NotImplementedError
