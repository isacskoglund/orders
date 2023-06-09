from typing import Callable
from domain.models.order import (
    RequestedOrder,
    VersionedOrder,
    PersistedOrder,
    Address,
    Item,
    VersionedItem,
)
from domain.models.order_status import Status
from domain.models.identifier import Identifier


def test_requested_order(
    product_version_ids: dict[Identifier, Identifier],
    requested_items: dict[Identifier, Item],
    versioned_items: dict[Identifier, VersionedItem],
    id_generator: Callable[[], Identifier],
    address: Address,
) -> None:
    customer_id = id_generator()
    requested_order = RequestedOrder(
        customer_id=customer_id,
        shipping_address=address,
        items=list(requested_items.values()),
    )

    versioned_order = requested_order.to_versioned_order(
        product_versions=product_version_ids
    )

    assert requested_order.get_product_ids() == [
        item.product_id for item in requested_items.values()
    ]
    assert versioned_order.customer_id == customer_id
    assert versioned_order.shipping_address == address
    assert versioned_order.items == list(versioned_items.values())


def test_versioned_order(
    versioned_items: list[VersionedItem],
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

    custom_status = Status.ACCEPTED_BY_INVENTORY

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
    versioned_items: list[VersionedItem],
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

    custom_status = Status.ACCEPTED_BY_INVENTORY
    updated_persisted_order = persisted_order.update_status(new_status=custom_status)

    for order in [persisted_order, updated_persisted_order]:
        assert order.id == persisted_order_id
        assert order.customer_id == customer_id
        assert order.shipping_address == address
        assert order.items == versioned_items
    assert persisted_order.status == Status.PENDING
    assert updated_persisted_order.status == custom_status
