from typing import Protocol
from dataclasses import dataclass
from models.product import ProductVersion


class AddProductVersionPort(Protocol):
    # Result

    @dataclass(frozen=True)
    class AddProductVersionResult:
        pass

    class ProductVersionAlreadyExitsResult(AddProductVersionResult):
        pass

    class ProductNotFoundById(AddProductVersionResult):
        pass

    class SuccessfullyAddedProductVersionResult(AddProductVersionResult):
        pass

    # Port

    def add_product_version(
        self, product_version: ProductVersion
    ) -> AddProductVersionResult:
        raise NotImplementedError
