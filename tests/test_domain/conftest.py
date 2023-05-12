from typing import Callable
from domain.models.identifier import Identifier
from domain.models.order import (
    PersistedOrder,
    Address,
    Item,
    VersionedItem,
    OrderData,
    ItemWithProductVersion,
)
from domain.models.product import ProductVersion
from pytest import fixture
from uuid import uuid4, UUID
from random import randint

MAX_PRICE = 10
ITEM_COUNT = 10
MAX_ITEM_QTY = 10


class IdentifierTest(Identifier):
    id: UUID = uuid4()


class AddressTest(Address):
    id: UUID = uuid4()


@fixture
def id_generator() -> Callable[[], Identifier]:
    return lambda: IdentifierTest()


@fixture
def address_generator() -> Callable[[], Address]:
    return lambda: AddressTest()


@fixture
def identifier() -> Identifier:
    return IdentifierTest()


@fixture
def address() -> Address:
    return AddressTest()


@fixture
def product_version_ids(
    id_generator: Callable[[], Identifier], item_count: int = ITEM_COUNT
) -> dict[Identifier, Identifier]:
    return {id_generator(): id_generator() for _ in range(0, item_count)}


@fixture
def product_versions(
    product_version_ids: dict[Identifier, Identifier], max_price: int = MAX_PRICE
) -> dict[Identifier, ProductVersion]:
    return {
        product_id: ProductVersion(
            id=product_version_id,
            product_id=product_id,
            price=ProductVersion.Price(
                amount=randint(1, max_price), unit="test_unit", currency="test_currency"
            ),
        )
        for product_id, product_version_id in product_version_ids.items()
    }


@fixture
def requested_items(
    product_version_ids: dict[Identifier, Identifier],
    max_item_qty: int = MAX_ITEM_QTY,
) -> dict[Identifier, Item]:
    return {
        product_id: Item(product_id=product_id, quantity=randint(1, max_item_qty))
        for product_id in product_version_ids.keys()
    }


@fixture
def versioned_items(
    requested_items: dict[Identifier, Item],
    product_version_ids: dict[Identifier, Identifier],
) -> dict[Identifier, VersionedItem]:
    return {
        product_id: VersionedItem(
            product_id=product_id,
            quantity=item.quantity,
            product_version_id=product_version_ids[product_id],
        )
        for product_id, item in requested_items.items()
    }


@fixture
def items_with_product_versions(
    requested_items: dict[Identifier, Item],
    product_versions: dict[Identifier, ProductVersion],
) -> dict[Identifier, ItemWithProductVersion]:
    return {
        product_id: ItemWithProductVersion(
            product_id=product_id,
            quantity=item.quantity,
            product_version=product_versions[product_id],
        )
        for product_id, item in requested_items.items()
    }


@fixture
def persisted_order(
    id_generator: Callable[[], Identifier],
    address: Address,
    versioned_items: dict[Identifier, VersionedItem],
) -> PersistedOrder:
    order_id = id_generator()
    customer_id = id_generator()
    order = PersistedOrder(
        id=order_id,
        customer_id=customer_id,
        items=list(versioned_items.values()),
        shipping_address=address,
    )
    return order


@fixture
def order_data(
    items_with_product_versions: dict[Identifier, ItemWithProductVersion],
    persisted_order: PersistedOrder,
) -> OrderData:
    order_data = OrderData(
        customer_id=persisted_order.customer_id,
        shipping_address=persisted_order.shipping_address,
        id=persisted_order.id,
        items=list(items_with_product_versions.values()),
        status=persisted_order.status,
    )
    return order_data
