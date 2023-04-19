from ports.spi.add_product_port import AddProductPort
from ports.spi.add_product_version_port import AddProductVersionPort
from ports.spi.update_product_current_product_version_port import (
    UpdateProductCurrentProductVersionPort,
)
from models.identifiers import ProductId, ProductVersionId
from models.product import Product, ProductVersion


class ProductCatalogueService(
    AddProductPort, AddProductVersionPort, UpdateProductCurrentProductVersionPort
):
    _add_product_port: AddProductPort
    _add_product_version_port: AddProductVersionPort
    _update_product_current_product_version_port: UpdateProductCurrentProductVersionPort

    def __init__(
        self,
        add_product_port: AddProductPort,
        add_product_version_port: AddProductVersionPort,
        update_product_current_product_version_port: UpdateProductCurrentProductVersionPort,
    ) -> None:
        self._add_product_port = add_product_port
        self._add_product_version_port = add_product_version_port
        self._update_product_current_product_version_port = (
            update_product_current_product_version_port
        )
        super().__init__()

    def add_product(self, product: Product) -> AddProductPort.AddProductResult:
        return self._add_product_port.add_product(self, product)

    def add_product_version(
        self, product_version: ProductVersion
    ) -> AddProductVersionPort.AddProductVersionResult:
        return super().add_product_version(product_version)

    def update_product_current_version(
        self, product_id: ProductId, new_product_version_id: ProductVersionId
    ) -> (
        UpdateProductCurrentProductVersionPort.UpdateProductCurrentProductVersionResult
    ):
        return super().update_product_current_version(
            product_id, new_product_version_id
        )
