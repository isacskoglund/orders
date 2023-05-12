from domain.services.place_order_service import PlaceOrderService
from domain.models.identifier import Identifier
from domain.models.order import (
    RequestedOrder,
    VersionedOrder,
    PersistedOrder,
    Address,
    Item,
)
from domain.models.event import DispatchableEvent
from domain.errors import InvalidProductIdError, NoCurrentProductVersionError
from test_domain.dummies import (
    SaveOrderDummy,
    GetProductVersionIdsDummy,
    EventDispatcherDummy,
    StatusToEventMapperDummy,
)
from typing import Callable
import pytest

# Tests:


def test_place_order_service_raises(
    product_version_ids: dict[Identifier, Identifier],
    id_generator: Callable[[], Identifier],
    requested_order: RequestedOrder,
    persisted_order: PersistedOrder,
) -> None:
    get_product_version_ids_dummy = GetProductVersionIdsDummy(
        product_version_ids=product_version_ids
    )
    save_order_dummy = SaveOrderDummy(persisted_order_to_return=persisted_order)
    event_dispatcher_dummy = EventDispatcherDummy()
    service = PlaceOrderService(
        get_product_version_ids_spi=get_product_version_ids_dummy,
        save_order_spi=save_order_dummy,
        event_dispatcher=event_dispatcher_dummy,
    )

    # Assert raises `InvalidProductIdError` on `invalid_ids` not empty:
    invalid_product_id = id_generator()
    get_product_version_ids_dummy.invalid_ids = {invalid_product_id}
    with pytest.raises(InvalidProductIdError) as error_info:
        service.place_order(requested_order=requested_order)
    assert error_info.value.product_id == invalid_product_id
    assert save_order_dummy.is_empty()
    assert event_dispatcher_dummy.is_empty()
    get_product_version_ids_dummy.invalid_ids = set()

    # Assert raises `NoCurrentProductVersionError` on `ids_without_product_version_id` not empty:
    product_id_without_product_version_id = id_generator()
    get_product_version_ids_dummy.ids_without_product_version_id = {
        product_id_without_product_version_id
    }
    with pytest.raises(NoCurrentProductVersionError) as error_info:
        service.place_order(requested_order=requested_order)
    assert error_info.value.product_id == product_id_without_product_version_id
    assert save_order_dummy.is_empty()
    assert event_dispatcher_dummy.is_empty()


def test_place_order_service_success(
    product_version_ids: dict[Identifier, Identifier],
    requested_order: RequestedOrder,
    versioned_order: VersionedOrder,
    persisted_order: PersistedOrder,
) -> None:
    get_product_version_ids_dummy = GetProductVersionIdsDummy()
    save_order_dummy = SaveOrderDummy(persisted_order_to_return=persisted_order)
    event_dispatcher_dummy = EventDispatcherDummy()
    status_to_event_mapper_dummy = StatusToEventMapperDummy()
    service = PlaceOrderService(
        get_product_version_ids_spi=get_product_version_ids_dummy,
        save_order_spi=save_order_dummy,
        event_dispatcher=event_dispatcher_dummy,
        _event_mapper=status_to_event_mapper_dummy,
    )

    # Setup:
    event_type = DispatchableEvent.EventType.CANCELLED
    expected_event = DispatchableEvent(order=persisted_order, event_type=event_type)
    status_to_event_mapper_dummy.event_type = event_type
    get_product_version_ids_dummy.product_version_ids = product_version_ids

    # Run:
    persisted_order_result = service.place_order(requested_order=requested_order)

    # Asserts:
    assert persisted_order_result == persisted_order
    assert save_order_dummy.read() == [versioned_order]
    assert event_dispatcher_dummy.read() == [expected_event]
