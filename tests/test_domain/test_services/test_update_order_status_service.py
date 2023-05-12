from domain.models.identifier import Identifier
from domain.models.order import PersistedOrder
from domain.models.order_status import Status
from domain.models.event import DispatchableEvent
from domain.ports.api.update_order_status_api import ExpectednessSetting
from domain.services.update_order_status_service import (
    UpdateOrderStatusService,
    TransitionValidator,
)
from domain.errors import InvalidOrderIdError, InsufficientExpectednessError
from test_domain.dummies import (
    UpdateOrderDummy,
    GetOrderByOrderIdDummy,
    EventDispatcherDummy,
    StatusToEventMapperDummy,
    TransitionValidatorDummy,
    TransitionDummy,
)
from typing import Callable
import pytest


@pytest.fixture
def transition_dummy() -> TransitionDummy:
    return TransitionDummy(from_status=Status.PENDING, to_status=Status.PENDING)


def test_transition_validator(transition_dummy: TransitionDummy) -> None:
    E = ExpectednessSetting

    def is_valid(setting: E):
        return TransitionValidator.validate_transition(
            transition=transition_dummy, setting=setting
        )

    # validate with all 4 available settings for each state of the dummy.

    transition_dummy.set_abnormal()
    assert is_valid(E.ALLOW_ABNORMAL) is True
    assert is_valid(E.ALLOW_UNEXPECTED) is False
    assert is_valid(E.REQUIRE_FORSEEN) is False
    assert is_valid(E.REQUIRE_NEXT_UP) is False

    transition_dummy.set_unexpected()
    assert is_valid(E.ALLOW_ABNORMAL) is True
    assert is_valid(E.ALLOW_UNEXPECTED) is True
    assert is_valid(E.REQUIRE_FORSEEN) is False
    assert is_valid(E.REQUIRE_NEXT_UP) is False

    transition_dummy.set_foreseen()
    assert is_valid(E.ALLOW_ABNORMAL) is True
    assert is_valid(E.ALLOW_UNEXPECTED) is True
    assert is_valid(E.REQUIRE_FORSEEN) is True
    assert is_valid(E.REQUIRE_NEXT_UP) is False

    transition_dummy.set_next_up()
    assert is_valid(E.ALLOW_ABNORMAL) is True
    assert is_valid(E.ALLOW_UNEXPECTED) is True
    assert is_valid(E.REQUIRE_FORSEEN) is True
    assert is_valid(E.REQUIRE_NEXT_UP) is True


def test_transition_validator_is_singleton() -> None:
    validator1 = TransitionValidator()
    validator2 = TransitionValidator()
    assert validator1 is validator2


def test_update_order_status_invalid_order_id(
    id_generator: Callable[[], Identifier],
) -> None:
    # Setup:
    update_order_dummy = UpdateOrderDummy()
    get_order_by_id_dummy = GetOrderByOrderIdDummy()
    event_dispatcher_dummy = EventDispatcherDummy()
    transition_validator_dummy = TransitionValidatorDummy()
    service = UpdateOrderStatusService(
        update_order_spi=update_order_dummy,
        get_order_by_order_id_spi=get_order_by_id_dummy,
        status_update_event_dispatcher_spi=event_dispatcher_dummy,
        _transition_validator=transition_validator_dummy,
    )
    order_id = id_generator()

    # Run:
    with pytest.raises(InvalidOrderIdError) as error_info:
        service.update_order_status(
            order_id=order_id, new_status=Status.ACCEPTED_BY_INVENTORY
        )

    # Asserts
    assert error_info.value.order_id == order_id
    assert update_order_dummy.is_empty()
    assert event_dispatcher_dummy.is_empty()


def test_update_order_status_invalid_transition(
    persisted_order: PersistedOrder,
) -> None:
    update_order_dummy = UpdateOrderDummy()
    get_order_by_id_dummy = GetOrderByOrderIdDummy()
    event_dispatcher_dummy = EventDispatcherDummy()
    transition_validator_dummy = TransitionValidatorDummy()

    # Setup:
    service = UpdateOrderStatusService(
        update_order_spi=update_order_dummy,
        get_order_by_order_id_spi=get_order_by_id_dummy,
        status_update_event_dispatcher_spi=event_dispatcher_dummy,
        _transition_validator=transition_validator_dummy,
    )
    get_order_by_id_dummy.orders = {persisted_order.id: persisted_order}
    transition_validator_dummy.set_invalid()

    # Run:
    with pytest.raises(InsufficientExpectednessError):
        service.update_order_status(
            order_id=persisted_order.id, new_status=Status.PENDING
        )

    # Asserts:
    assert update_order_dummy.is_empty()
    assert event_dispatcher_dummy.is_empty()


def test_update_order_status_success(
    persisted_order: PersistedOrder,
) -> None:
    # Setup:
    update_order_dummy = UpdateOrderDummy()
    get_order_by_id_dummy = GetOrderByOrderIdDummy()
    event_dispatcher_dummy = EventDispatcherDummy()
    transition_validator_dummy = TransitionValidatorDummy()
    status_to_event_mapper_dummy = StatusToEventMapperDummy()
    service = UpdateOrderStatusService(
        update_order_spi=update_order_dummy,
        get_order_by_order_id_spi=get_order_by_id_dummy,
        status_update_event_dispatcher_spi=event_dispatcher_dummy,
        _status_to_event_mapper=status_to_event_mapper_dummy,
        _transition_validator=transition_validator_dummy,
    )
    get_order_by_id_dummy.orders = {persisted_order.id: persisted_order}
    transition_validator_dummy.set_valid()
    new_status = Status.ACCEPTED_BY_INVENTORY
    expected_result = persisted_order.update_status(new_status=new_status)
    expected_event_type = DispatchableEvent.EventType.CANCELLED
    status_to_event_mapper_dummy.event_type = expected_event_type

    # Run:
    result = service.update_order_status(
        order_id=persisted_order.id, new_status=new_status
    )

    # Asserts:
    assert result == expected_result
    assert update_order_dummy.read() == {persisted_order.id: new_status}
    assert event_dispatcher_dummy.read() == [
        DispatchableEvent(order=expected_result, event_type=expected_event_type)
    ]
