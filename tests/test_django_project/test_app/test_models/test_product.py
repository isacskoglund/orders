from tests.test_django_project.factories import ProductFactory, ProductVersionFactory
from app.models import Product, ProductVersion

import pytest
from uuid import UUID


def test_product_default_id() -> None:
    product = Product()
    assert isinstance(product.id, UUID)


def test_product_version_default_id() -> None:
    product_version = ProductVersion()
    assert isinstance(product_version.id, UUID)


@pytest.mark.django_db
def test_product_with_product_version(
    product_factory: ProductFactory,
    product_version_factory: ProductVersionFactory,
) -> None:
    # Arrange
    product: Product = product_factory.create()
    product_version: ProductVersion = product_version_factory.create(product=product)

    # Act
    product.current_product_version = product_version
    product.save()

    product_res = Product.objects.first()
    product_version_res = ProductVersion.objects.first()

    # Assert
    assert product == product_res
    assert product_version == product_version_res
    assert product.current_product_version == product_version
    assert product_version.product == product
