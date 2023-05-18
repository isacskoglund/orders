from typing import Callable
from domain.models.identifier import Identifier
from domain.models.order import (
    RequestedOrder,
    VersionedOrder,
    PersistedOrder,
    OrderData,
    Address,
    Item,
    VersionedItem,
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


# PRODUCT VERSION IDS:


@fixture
def product_version_ids(
    id_generator: Callable[[], Identifier], item_count: int = ITEM_COUNT
) -> dict[Identifier, Identifier]:
    """
    Returns a dict that maps `product_id` to `product_version_id`.
    """
    return {id_generator(): id_generator() for _ in range(0, item_count)}


# PRODUCT VERSIONS:


@fixture
def product_versions(
    product_version_ids: dict[Identifier, Identifier], max_price: int = MAX_PRICE
) -> dict[Identifier, ProductVersion]:
    """
    Returns a dict that maps `product_version_id` to instances of `ProductVersion`.
    """
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


# ORDER ITEMS:


@fixture
def requested_items(
    product_version_ids: dict[Identifier, Identifier],
    max_item_qty: int = MAX_ITEM_QTY,
) -> dict[Identifier, Item]:
    """
    Returns dict that maps `product_id` to instances of `Item`.
    """
    return {
        product_id: Item(product_id=product_id, quantity=randint(1, max_item_qty))
        for product_id in product_version_ids.keys()
    }


@fixture
def versioned_items(
    requested_items: dict[Identifier, Item],
    product_version_ids: dict[Identifier, Identifier],
) -> dict[Identifier, VersionedItem]:
    """
    Returns dict that maps `product_id` to instances of `VersionedItem`.
    Copies common attributes from `requested_items`.
    """
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
    """
    Returns dict that maps `product_id` to instances of `ItemWithProductVersion`.
    Copies common attributes from `requested_items`.
    """
    return {
        product_id: ItemWithProductVersion(
            product_id=product_id,
            quantity=item.quantity,
            product_version=product_versions[product_id],
        )
        for product_id, item in requested_items.items()
    }


# ORDERS:


@fixture
def requested_order(
    id_generator: Callable[[], Identifier],
    address: Address,
    requested_items: dict[Identifier, Item],
) -> RequestedOrder:
    """
    Returns instance of `RequestedOrder`. Randomizes `customer_id`.
    """
    customer_id = id_generator()
    return RequestedOrder(
        customer_id=customer_id,
        shipping_address=address,
        items=list(requested_items.values()),
    )


@fixture
def versioned_order(
    requested_order: RequestedOrder, versioned_items: dict[Identifier, VersionedItem]
) -> VersionedOrder:
    """
    Returns instance of `VersionedOrder`. Copies common attributes from requested_order.
    """
    return VersionedOrder(
        customer_id=requested_order.customer_id,
        shipping_address=requested_order.shipping_address,
        items=list(versioned_items.values()),
    )


@fixture
def persisted_order(
    id_generator: Callable[[], Identifier],
    address: Address,
    versioned_order: VersionedOrder,
) -> PersistedOrder:
    """
    Returns instance of `PersistedOrder`.
    Copies `customer_id` and `items` from `versioned_order`. Randomizes `order_id`.
    """
    order_id = id_generator()
    return PersistedOrder(
        id=order_id,
        customer_id=versioned_order.customer_id,
        items=versioned_order.items,
        shipping_address=address,
    )


@fixture
def order_data(
    items_with_product_versions: dict[Identifier, ItemWithProductVersion],
    persisted_order: PersistedOrder,
) -> OrderData:
    """
    Returns instance of `OrderData`. Copies common attributes from `persisted_order`.
    """
    return OrderData(
        customer_id=persisted_order.customer_id,
        shipping_address=persisted_order.shipping_address,
        id=persisted_order.id,
        items=list(items_with_product_versions.values()),
        status=persisted_order.status,
    )
