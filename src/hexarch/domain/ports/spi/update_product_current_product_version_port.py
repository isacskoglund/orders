from typing import Protocol
from dataclasses import dataclass
from models.identifiers import ProductId, ProductVersionId


class UpdateProductCurrentProductVersionPort:
    # Results:

    @dataclass
    class UpdateProductCurrentProductVersionResult:
        pass

    class ProductVersionNotFoundById(UpdateProductCurrentProductVersionResult):
        pass

    class SuccessfullyUpdatedCurrentProductVersionResult(
        UpdateProductCurrentProductVersionResult
    ):
        pass

    # Port:

    def update_product_current_version(
        self, product_id: ProductId, new_product_version_id: ProductVersionId
    ) -> UpdateProductCurrentProductVersionResult:
        raise NotImplementedError
