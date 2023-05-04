from typing import Callable
from uuid import uuid4, UUID
from domain.models.order import RequestedOrder, VersionedOrder, PersistedOrder, Address
from domain.models.order_status import Status
from domain.models.identifier import Identifier
import random


def test_requested_order(
    product_versions: dict[Identifier, Identifier],
    requested_items: list[RequestedOrder.Item],
    versioned_items: list[VersionedOrder.Item],
    id_generator: Callable[[], Identifier],
    address: Address,
) -> None:
    customer_id = id_generator()
    requested_order = RequestedOrder(
        customer_id=customer_id,
        shipping_address=address,
        items=requested_items,
    )

    versioned_order = requested_order.to_versioned_order(
        product_versions=product_versions
    )

    assert requested_order.get_product_ids() == [
        item.product_id for item in requested_items
    ]
    assert versioned_order.customer_id == customer_id
    assert versioned_order.shipping_address == address
    assert versioned_order.items == versioned_items


def test_versioned_order(
    versioned_items: list[VersionedOrder.Item],
    id_generator: Callable[[], Identifier],
    address: Address,
) -> None:
    customer_id = id_generator()
    persisted_order_id = id_generator()

    versioned_order = VersionedOrder(
        customer_id=customer_id,
        shipping_address=address,
        items=versioned_items,
    )

    custom_status = random.choice(list(Status))

    default_status_persisted_order = versioned_order.to_persisted_order(
        id=persisted_order_id
    )

    custom_status_persisted_order = versioned_order.to_persisted_order(
        id=persisted_order_id, status=custom_status
    )

    for order in [default_status_persisted_order, custom_status_persisted_order]:
        assert order.customer_id == customer_id
        assert order.shipping_address == address
        assert order.items == versioned_items
        assert order.id == persisted_order_id
    assert default_status_persisted_order.status == Status.PENDING
    assert custom_status_persisted_order.status == custom_status


def test_persisted_order(
    versioned_items: list[VersionedOrder.Item],
    id_generator: Callable[[], Identifier],
    address: Address,
) -> None:
    persisted_order_id = id_generator()
    customer_id = id_generator()
    persisted_order = PersistedOrder(
        id=persisted_order_id,
        customer_id=customer_id,
        items=versioned_items,
        shipping_address=address,
    )

    custom_status = random.choice(list(Status))
    updated_persisted_order = persisted_order.update_status(new_status=custom_status)

    for order in [persisted_order, updated_persisted_order]:
        assert order.id == persisted_order_id
        assert order.customer_id == customer_id
        assert order.shipping_address == address
        assert order.items == versioned_items
    assert persisted_order.status == Status.PENDING
    assert updated_persisted_order.status == custom_status
