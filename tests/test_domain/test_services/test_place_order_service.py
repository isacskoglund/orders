from domain.services.place_order_service import PlaceOrderService
from domain.models.identifier import Identifier
from domain.models.order import RequestedOrder, VersionedOrder, PersistedOrder
from domain.errors import InvalidProductIdError, NoCurrentProductVersionError
from conftest import (
    SaveOrderDummy,
    GetProductVersionIdsDummy,
    EventDispatcherDummy,
    StatusToEventMapperDummy,
    EventTest,
)
from typing import Callable
from random import randint
from pytest import fixture
import pytest

MAX_ORDER_ITEM_QUANTITY = 10


# Product Ids:


@fixture
def product_ids_to_version_ids(
    product_versions: dict[Identifier, Identifier]
) -> dict[Identifier, Identifier]:
    return product_versions


@fixture
def invalid_product_id(id_generator: Callable[[], Identifier]) -> Identifier:
    return id_generator()


@fixture
def valid_product_id_with_missing_product_version(
    id_generator: Callable[[], Identifier]
) -> Identifier:
    return id_generator()


# Order Items:


@fixture
def valid_items(
    product_ids_to_version_ids: dict[Identifier, Identifier]
) -> list[RequestedOrder.Item]:
    return [
        RequestedOrder.Item(
            product_id=product_id, quantity=randint(0, MAX_ORDER_ITEM_QUANTITY)
        )
        for product_id in product_ids_to_version_ids
    ]


@fixture
def invalid_item(invalid_product_id) -> RequestedOrder.Item:
    return RequestedOrder.Item(
        product_id=invalid_product_id, quantity=randint(0, MAX_ORDER_ITEM_QUANTITY)
    )


@fixture
def valid_item_with_missing_product_version(
    valid_product_id_with_missing_product_version,
) -> RequestedOrder.Item:
    return RequestedOrder.Item(
        product_id=valid_product_id_with_missing_product_version,
        quantity=randint(0, MAX_ORDER_ITEM_QUANTITY),
    )


# Orders:


@fixture
def valid_order(valid_items, id_generator, address_generator) -> RequestedOrder:
    return RequestedOrder(
        customer_id=id_generator(),
        shipping_address=address_generator(),
        items=valid_items,
    )


@fixture
def invalid_order(
    valid_items, invalid_item, id_generator, address_generator
) -> RequestedOrder:
    return RequestedOrder(
        customer_id=id_generator(),
        shipping_address=address_generator(),
        items=[*valid_items, invalid_item],
    )


@fixture
def valid_order_with_missing_product_version(
    valid_items,
    valid_item_with_missing_product_version,
    id_generator,
    address_generator,
) -> RequestedOrder:
    return RequestedOrder(
        customer_id=id_generator(),
        shipping_address=address_generator(),
        items=[*valid_items, valid_item_with_missing_product_version],
    )


@fixture
def valid_versioned_order(
    valid_order: RequestedOrder, product_ids_to_version_ids
) -> VersionedOrder:
    return valid_order.to_versioned_order(product_versions=product_ids_to_version_ids)


# Tests:


def test_place_order_service_invalid_product_id(
    get_product_version_ids_dummy: GetProductVersionIdsDummy,
    save_order_dummy: SaveOrderDummy,
    event_dispatcher_dummy: EventDispatcherDummy,
    product_ids_to_version_ids: dict[Identifier, Identifier],
    invalid_product_id: Identifier,
    invalid_order: RequestedOrder,
) -> None:
    service = PlaceOrderService(
        get_product_version_ids_spi=get_product_version_ids_dummy,
        save_order_spi=save_order_dummy,
        event_dispatcher=event_dispatcher_dummy,
    )
    get_product_version_ids_dummy.set(product_version_ids=product_ids_to_version_ids)
    with pytest.raises(InvalidProductIdError) as error_info:
        service.place_order(requested_order=invalid_order)
    assert error_info.value.product_id == invalid_product_id
    assert save_order_dummy.is_empty()
    assert event_dispatcher_dummy.is_empty()


def test_place_order_service_valid_id_without_version(
    get_product_version_ids_dummy: GetProductVersionIdsDummy,
    save_order_dummy: SaveOrderDummy,
    event_dispatcher_dummy: EventDispatcherDummy,
    product_ids_to_version_ids: dict[Identifier, Identifier],
    valid_product_id_with_missing_product_version: Identifier,
    valid_order_with_missing_product_version: RequestedOrder,
) -> None:
    service = PlaceOrderService(
        get_product_version_ids_spi=get_product_version_ids_dummy,
        save_order_spi=save_order_dummy,
        event_dispatcher=event_dispatcher_dummy,
    )
    get_product_version_ids_dummy.set(
        product_version_ids={
            **product_ids_to_version_ids,
            valid_product_id_with_missing_product_version: None,
        }
    )
    with pytest.raises(NoCurrentProductVersionError) as error_info:
        service.place_order(requested_order=valid_order_with_missing_product_version)
    assert error_info.value.product_id == valid_product_id_with_missing_product_version
    assert save_order_dummy.is_empty()
    assert event_dispatcher_dummy.is_empty()


def test_place_order_service_success(
    get_product_version_ids_dummy: GetProductVersionIdsDummy,
    save_order_dummy: SaveOrderDummy,
    event_dispatcher_dummy: EventDispatcherDummy,
    product_ids_to_version_ids: dict[Identifier, Identifier],
    valid_order: RequestedOrder,
    valid_versioned_order: VersionedOrder,
    status_to_event_mapper_dummy: StatusToEventMapperDummy,
) -> None:
    service = PlaceOrderService(
        get_product_version_ids_spi=get_product_version_ids_dummy,
        save_order_spi=save_order_dummy,
        event_dispatcher=event_dispatcher_dummy,
        _event_mapper=status_to_event_mapper_dummy,
    )
    status_to_event_mapper_dummy.event_type = EventTest
    get_product_version_ids_dummy.set(product_version_ids=product_ids_to_version_ids)
    save_order_dummy.reset()
    event_dispatcher_dummy.reset()

    service.place_order(requested_order=valid_order)

    saved_orders = save_order_dummy.read()
    assert len(saved_orders) == 1
    expected_order_id = next(iter(saved_orders))
    expected_persisted_order = valid_versioned_order.to_persisted_order(
        id=expected_order_id
    )
    assert expected_persisted_order == saved_orders[expected_order_id]

    dispatched_events = event_dispatcher_dummy.read()
    assert len(dispatched_events) == 1
    assert dispatched_events[0].order == expected_persisted_order
