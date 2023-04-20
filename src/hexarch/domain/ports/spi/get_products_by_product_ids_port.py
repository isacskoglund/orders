from typing import Protocol
from dataclasses import dataclass
from models.identifiers import ProductId
from models.product import Product


class GetProductsByProductIdsPort(Protocol):
    # Result
    @dataclass
    class GetProductByProductIdResult:
        pass

    class ProductNotFoundResult:
        product_ids_not_found: list[ProductId]

    class SuccessfullyGotProductByIdResult:
        product_id: ProductId

    # Port
    def get_products_by_product_ids(
        self, product_ids: list[ProductId]
    ) -> list[Product]:
        raise NotImplementedError
