from typing import Protocol
from dataclasses import dataclass
from models.product import Product


class AddProductPort(Protocol):
    # Result:

    @dataclass
    class AddProductResult:
        pass

    class ProductAlreadyExistsResult(AddProductResult):
        pass

    class SuccessfullyAddedProductResult(AddProductResult):
        pass

    # Port

    def add_product(product: Product) -> AddProductResult:
        raise NotImplementedError
