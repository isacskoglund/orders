from typing import Callable
from domain.models.identifier import Identifier
from domain.models.order import (
    VersionedOrder,
    PersistedOrder,
    Address,
    Item,
    VersionedItem,
)
from pytest import fixture
from uuid import uuid4, UUID
from random import choice, randint


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
def product_versions(
    id_generator: Callable[[], Identifier], size: int = 10
) -> dict[Identifier, Identifier]:
    result: dict[Identifier, Identifier] = {}
    for _ in range(0, size):
        result[id_generator()] = id_generator()
    return result


@fixture
def requested_items(
    product_versions: dict[Identifier, Identifier],
    size: int = 5,
    max_quantity: int = 10,
) -> list[Item]:
    result: list[Item] = []
    for _ in range(0, size):
        product_id = choice(list(product_versions.keys()))
        item = Item(product_id=product_id, quantity=randint(1, max_quantity))
        result.append(item)
    return result


@fixture
def versioned_items(
    requested_items: list[Item],
    product_versions: dict[Identifier, Identifier],
) -> list[VersionedItem]:
    return [
        VersionedItem(
            product_id=item.product_id,
            quantity=item.quantity,
            product_version_id=product_versions[item.product_id],
        )
        for item in requested_items
    ]


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
