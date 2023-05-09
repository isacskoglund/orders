from typing import Callable
from domain.models.identifier import Identifier
from domain.models.order import RequestedOrder, VersionedOrder, PersistedOrder, Address
from pytest import fixture
from uuid import uuid4, UUID
from random import choice, randint


class IdentifierTest(Identifier):
    id: UUID = uuid4()


class AddressTest(Address):
    id: UUID = uuid4()


@fixture
def id_generator() -> Callable[[], IdentifierTest]:
    return lambda: IdentifierTest()


@fixture
def address_generator() -> Callable[[], AddressTest]:
    return lambda: AddressTest()


@fixture
def identifier() -> IdentifierTest:
    return IdentifierTest()


@fixture
def address() -> AddressTest:
    return AddressTest()


@fixture
def product_versions(
    id_generator: Callable[[], Identifier], size: int = 10
) -> dict[IdentifierTest, IdentifierTest]:
    result = {}
    for _ in range(0, size):
        result[id_generator()] = id_generator()
    return result


@fixture
def requested_items(
    product_versions: dict[IdentifierTest, IdentifierTest],
    size: int = 5,
    max_quantity: int = 10,
) -> list[RequestedOrder.Item]:
    result = []
    for _ in range(0, size):
        product_id = choice(list(product_versions.keys()))
        item = RequestedOrder.Item(
            product_id=product_id, quantity=randint(1, max_quantity)
        )
        result.append(item)
    return result


@fixture
def versioned_items(
    requested_items: list[RequestedOrder.Item],
    product_versions: dict[IdentifierTest, IdentifierTest],
) -> list[VersionedOrder.Item]:
    return [
        VersionedOrder.Item(
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
    versioned_items: list[VersionedOrder.Item],
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
