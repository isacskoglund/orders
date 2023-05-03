from uuid import uuid4, UUID
from domain.models.order import RequestedOrder, VersionedOrder, PersistedOrder, Address
from domain.models.user import Customer
from domain.models.identifiers import CustomerId, ProductId, ProductVersionId, OrderId
from domain.models.product import Product, ProductVersion
import random
import pytest


class CustomerIdTest(CustomerId):
    id = uuid4()


class ProductIdTest(ProductId):
    id = uuid4()


class ProductVersionIdTest(ProductVersionId):
    id = uuid4()


class OrderIdTest(OrderId):
    id = uuid4()


class AddressTest(Address):
    id = uuid4()


@pytest.fixture
def product_versions(size: int = 10) -> dict[ProductIdTest, ProductVersionIdTest]:
    result = {}
    for i in range(0, size):
        result[ProductIdTest()] = ProductVersionIdTest()
    return result


@pytest.fixture
def requested_items(
    product_versions: dict[ProductIdTest, ProductVersionIdTest],
    size: int = 5,
    max_quantity: int = 10,
) -> list[RequestedOrder.Item]:
    result = []
    for i in range(0, size):
        product_id = random.choice(list(product_versions.keys()))
        item = RequestedOrder.Item(
            product_id=product_id, quantity=random.randint(1, max_quantity)
        )
        result.append(item)
    return result


@pytest.fixture
def versioned_items(
    requested_items: list[RequestedOrder.Item],
    product_versions: dict[ProductIdTest, ProductVersionIdTest],
) -> list[VersionedOrder.Item]:
    return [
        VersionedOrder.Item(
            product_id=item.product_id,
            quantity=item.quantity,
            product_version_id=product_versions[item.product_id],
        )
        for item in requested_items
    ]


def test_requested_order(
    product_versions: dict[ProductIdTest, ProductVersionIdTest],
    requested_items: list[RequestedOrder.Item],
    versioned_items: list[VersionedOrder.Item],
) -> None:
    customer_id = CustomerIdTest()
    shipping_address = AddressTest()
    requested_order = RequestedOrder(
        customer_id=customer_id,
        shipping_address=shipping_address,
        items=requested_items,
    )

    versioned_order = requested_order.to_versioned_order(
        product_versions=product_versions
    )

    assert requested_order.get_product_ids() == [
        item.product_id for item in requested_items
    ]
    assert versioned_order.customer_id == customer_id
    assert versioned_order.shipping_address == shipping_address
    assert versioned_order.items == versioned_items


def test_versioned_order(versioned_items: list[VersionedOrder.Item]) -> None:
    customer_id = CustomerIdTest()
    shipping_address = AddressTest()

    versioned_order = VersionedOrder(
        customer_id=customer_id,
        shipping_address=shipping_address,
        items=versioned_items,
    )

    persisted_order_id = OrderIdTest()
    custom_status = random.choice(list(PersistedOrder.Status))

    default_status_persisted_order = versioned_order.to_persisted_order(
        id=persisted_order_id
    )

    custom_status_persisted_order = versioned_order.to_persisted_order(
        id=persisted_order_id, status=custom_status
    )

    for order in [default_status_persisted_order, custom_status_persisted_order]:
        assert order.customer_id == customer_id
        assert order.shipping_address == shipping_address
        assert order.items == versioned_items
        assert order.id == persisted_order_id
    assert default_status_persisted_order.status == PersistedOrder.Status.REQUESTED
    assert custom_status_persisted_order.status == custom_status


def test_persisted_order(versioned_items: list[VersionedOrder.Item]) -> None:
    persisted_order_id = OrderIdTest()
    customer_id = CustomerIdTest()
    shipping_address = AddressTest()
    persisted_order = PersistedOrder(
        id=persisted_order_id,
        customer_id=customer_id,
        items=versioned_items,
        shipping_address=shipping_address,
    )

    custom_status = random.choice(list(PersistedOrder.Status))
    updated_persisted_order = persisted_order.update_status(new_status=custom_status)

    for order in [persisted_order, updated_persisted_order]:
        assert order.id == persisted_order_id
        assert order.customer_id == customer_id
        assert shipping_address == shipping_address
        assert order.items == versioned_items
    assert persisted_order.status == PersistedOrder.Status.REQUESTED
    assert updated_persisted_order.status == custom_status
