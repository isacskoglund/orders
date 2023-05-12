from domain.services.place_order_service import PlaceOrderService
from domain.models.identifier import Identifier
from domain.models.order import (
    RequestedOrder,
    VersionedOrder,
    PersistedOrder,
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
from dataclasses import dataclass
import pytest


# Tests:
@dataclass
class Dummies:
    get_product_version_ids_dummy: GetProductVersionIdsDummy
    save_order_dummy: SaveOrderDummy
    event_dispatcher_dummy: EventDispatcherDummy
    status_to_event_mapper_dummy: StatusToEventMapperDummy


@pytest.fixture
def dummies(
    product_version_ids: dict[Identifier, Identifier], persisted_order: PersistedOrder
) -> Dummies:
    dummies = Dummies(
        get_product_version_ids_dummy=GetProductVersionIdsDummy(
            product_version_ids=product_version_ids
        ),
        save_order_dummy=SaveOrderDummy(persisted_order_to_return=persisted_order),
        event_dispatcher_dummy=EventDispatcherDummy(),
        status_to_event_mapper_dummy=StatusToEventMapperDummy(),
    )
    return dummies


@pytest.fixture
def service(dummies: Dummies) -> PlaceOrderService:
    return PlaceOrderService(
        get_product_version_ids_spi=dummies.get_product_version_ids_dummy,
        save_order_spi=dummies.save_order_dummy,
        event_dispatcher=dummies.event_dispatcher_dummy,
        _event_mapper=dummies.status_to_event_mapper_dummy,
    )


class TestPlaceOrderService:
    @staticmethod
    def test_raise_on_invalid_product_id(
        id_generator: Callable[[], Identifier],
        requested_order: RequestedOrder,
        dummies: Dummies,
        service: PlaceOrderService,
    ) -> None:
        """
        Assert that service raises `InvalidProductIdError`
        on `invalid_ids` not empty,
        and that the content of the order is correct.
        """

        invalid_product_id = id_generator()
        dummies.get_product_version_ids_dummy.invalid_ids = {invalid_product_id}

        with pytest.raises(InvalidProductIdError) as error_info:
            service.place_order(requested_order=requested_order)
        assert error_info.value.product_id == invalid_product_id
        assert dummies.save_order_dummy.is_empty()
        assert dummies.event_dispatcher_dummy.is_empty()

    @staticmethod
    def test_raise_on_product_id_without_current_product_version_id(
        id_generator: Callable[[], Identifier],
        requested_order: RequestedOrder,
        dummies: Dummies,
        service: PlaceOrderService,
    ) -> None:
        """
        Assert service raises `NoCurrentProductVersionError`
        on `ids_without_product_version_id` not empty,
        and that the content of the error is correct.
        """

        product_id_without_product_version_id = id_generator()
        dummies.get_product_version_ids_dummy.ids_without_product_version_id = {
            product_id_without_product_version_id
        }

        with pytest.raises(NoCurrentProductVersionError) as error_info:
            service.place_order(requested_order=requested_order)
        assert error_info.value.product_id == product_id_without_product_version_id
        assert dummies.save_order_dummy.is_empty()
        assert dummies.event_dispatcher_dummy.is_empty()

    @staticmethod
    def test_place_order_success(
        product_version_ids: dict[Identifier, Identifier],
        requested_order: RequestedOrder,
        versioned_order: VersionedOrder,
        persisted_order: PersistedOrder,
        dummies: Dummies,
        service: PlaceOrderService,
    ) -> None:
        """
        Assert that saving to persistence, dispatching events
        and returning instance of `PersistedOrder` works as expected.
        """

        event_type = DispatchableEvent.EventType.CANCELLED
        expected_event = DispatchableEvent(order=persisted_order, event_type=event_type)
        dummies.status_to_event_mapper_dummy.event_type = event_type
        dummies.get_product_version_ids_dummy.product_version_ids = product_version_ids

        # Run:
        persisted_order_result = service.place_order(requested_order=requested_order)

        # Asserts:
        assert persisted_order_result == persisted_order
        assert dummies.save_order_dummy.read() == [versioned_order]
        assert dummies.event_dispatcher_dummy.read() == [expected_event]
