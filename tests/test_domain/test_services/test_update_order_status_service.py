from domain.models.identifier import Identifier
from domain.models.order import PersistedOrder
from domain.models.order_status import Status
from domain.models.event import DispatchableEvent
from domain.services.update_order_status_service import (
    UpdateOrderStatusService,
)
from domain.errors import InvalidOrderIdError, InsufficientExpectednessError
from test_domain.dummies import (
    UpdateOrderDummy,
    GetOrderByOrderIdDummy,
    EventDispatcherDummy,
    StatusToEventMapperDummy,
    TransitionValidatorDummy,
)
from typing import Callable
from dataclasses import dataclass
import pytest


@dataclass
class Dummies:
    update_order_dummy: UpdateOrderDummy
    get_order_by_id_dummy: GetOrderByOrderIdDummy
    event_dispatcher_dummy: EventDispatcherDummy
    transition_validator_dummy: TransitionValidatorDummy
    status_to_event_mapper_dummy: StatusToEventMapperDummy


@pytest.fixture
def dummies() -> Dummies:
    return Dummies(
        update_order_dummy=UpdateOrderDummy(),
        get_order_by_id_dummy=GetOrderByOrderIdDummy(),
        event_dispatcher_dummy=EventDispatcherDummy(),
        transition_validator_dummy=TransitionValidatorDummy(),
        status_to_event_mapper_dummy=StatusToEventMapperDummy(),
    )


@pytest.fixture
def service(dummies: Dummies) -> UpdateOrderStatusService:
    return UpdateOrderStatusService(
        update_order_spi=dummies.update_order_dummy,
        get_order_by_order_id_spi=dummies.get_order_by_id_dummy,
        status_update_event_dispatcher_spi=dummies.event_dispatcher_dummy,
        _transition_validator=dummies.transition_validator_dummy,
        _status_to_event_mapper=dummies.status_to_event_mapper_dummy,
    )


def test_update_order_status_invalid_order_id(
    id_generator: Callable[[], Identifier],
    dummies: Dummies,
    service: UpdateOrderStatusService,
) -> None:
    """
    Assert that service raises `InvalidOrderIdError`
    when persistence returns `None` instead of an order.
    """

    # Setup:
    order_id = id_generator()

    # Run:
    with pytest.raises(InvalidOrderIdError) as error_info:
        service.update_order_status(order_id=order_id, new_status=Status.PENDING)

    # Assert:
    assert error_info.value.order_id == order_id
    assert dummies.update_order_dummy.is_empty()
    assert dummies.event_dispatcher_dummy.is_empty()


def test_update_order_status_invalid_transition(
    persisted_order: PersistedOrder,
    dummies: Dummies,
    service: UpdateOrderStatusService,
) -> None:
    """
    Assert that service raises `InsufficientExpectednessError`
    when the transition validator rejects the transition.
    """

    # Setup:
    dummies.get_order_by_id_dummy.orders = {persisted_order.id: persisted_order}
    dummies.transition_validator_dummy.set_invalid()

    # Run:
    with pytest.raises(InsufficientExpectednessError):
        service.update_order_status(
            order_id=persisted_order.id, new_status=Status.PENDING
        )

    # Assert:
    assert dummies.update_order_dummy.is_empty()
    assert dummies.event_dispatcher_dummy.is_empty()


def test_update_order_status_success(
    persisted_order: PersistedOrder,
    dummies: Dummies,
    service: UpdateOrderStatusService,
) -> None:
    """
    Assert that updating the order to persistence, dispatching events
    and returning instance of `PersistedOrder` with new status works as
    expected.
    """

    # Setup:
    dummies.get_order_by_id_dummy.orders = {persisted_order.id: persisted_order}
    dummies.transition_validator_dummy.set_valid()
    new_status = Status.ACCEPTED_BY_INVENTORY
    expected_result = persisted_order.update_status(new_status=new_status)
    event_type = DispatchableEvent.EventType.CANCELLED
    expected_event = DispatchableEvent(order=expected_result, event_type=event_type)
    dummies.status_to_event_mapper_dummy.event_type = event_type

    # Run:
    result = service.update_order_status(
        order_id=persisted_order.id, new_status=new_status
    )

    # Assert:
    assert result == expected_result
    assert dummies.update_order_dummy.read() == {persisted_order.id: new_status}
    assert dummies.event_dispatcher_dummy.read() == [expected_event]
