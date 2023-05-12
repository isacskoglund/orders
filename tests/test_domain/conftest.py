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
from random import choice, randint

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
    id_generator: Callable[[], Identifier], size: int = 10
) -> dict[Identifier, Identifier]:
    result: dict[Identifier, Identifier] = {}
    for _ in range(0, size):
        result[id_generator()] = id_generator()
    return result


@fixture
def product_versions(
    product_version_ids: dict[Identifier, Identifier]
) -> dict[Identifier, ProductVersion]:
    result: dict[Identifier, ProductVersion] = {}
    for product_id, product_version_id in product_version_ids.items():
        result[product_id] = ProductVersion(
            id=product_version_id,
            product_id=product_id,
            price=ProductVersion.Price(
                amount=randint(1, MAX_PRICE), unit="test_unit", currency="test_currency"
            ),
        )
    return result


@fixture
def requested_items(
    product_version_ids: dict[Identifier, Identifier],
    max_item_qty: int = MAX_ITEM_QTY,
) -> dict[Identifier, Item]:
    result: dict[Identifier, Item] = {}
    for product_id in product_version_ids.keys():
        item = Item(product_id=product_id, quantity=randint(1, max_item_qty))
        result[product_id] = item
    return result


@fixture
def versioned_items(
    requested_items: dict[Identifier, Item],
    product_version_ids: dict[Identifier, Identifier],
) -> list[VersionedItem]:
    return [
        VersionedItem(
            product_id=product_id,
            quantity=item.quantity,
            product_version_id=product_version_ids[product_id],
        )
        for product_id, item in requested_items.items()
    ]


@fixture
def items_with_product_versions(
    product_version_ids: dict[Identifier, Identifier],
    product_versions: dict[Identifier, ProductVersion],
    max_item_qty: int = MAX_ITEM_QTY,
) -> dict[Identifier, ItemWithProductVersion]:
    result: dict[Identifier, ItemWithProductVersion] = {}
    for product_id in product_version_ids.keys():
        result[product_id] = ItemWithProductVersion(
            product_id=product_id,
            quantity=randint(1, MAX_ITEM_QTY),
            product_version=product_versions[product_id],
        )
    return result


@fixture
def persisted_order(
    id_generator: Callable[[], Identifier],
    address: Address,
    versioned_items: list[VersionedItem],
) -> PersistedOrder:
    order_id = id_generator()
    customer_id = id_generator()
    order = PersistedOrder(
        id=order_id,
        customer_id=customer_id,
        items=versioned_items,
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
