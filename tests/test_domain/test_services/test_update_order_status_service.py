from domain.models.event import StatusToEventMapper
from domain.models.identifier import Identifier
from domain.models.order import PersistedOrder
from domain.models.order_status import Status, StatusTransitionProtocol
from domain.ports.api.update_order_status_api import ExpectednessSetting
from domain.services.update_order_status_service import (
    UpdateOrderStatusService,
    _validate_transition,
)
from domain.errors import InvalidOrderIdError, InsufficientExpectednessError
from conftest import (
    UpdateOrderDummy,
    GetOrderByOrderIdDummy,
    EventDispatcherDummy,
    StatusToEventMapperDummy,
)
from dataclasses import dataclass
from typing import Callable
import pytest


@dataclass
class TransitionDummy(StatusTransitionProtocol):
    from_status: Status
    to_status: Status
    is_abnormal: bool = False
    is_unexpected: bool = False
    is_foreseen: bool = False
    is_next_up: bool = False

    def set_abnormal(self) -> None:
        self.is_abnormal = True
        self.is_unexpected = True
        self.is_foreseen = False
        self.is_next_up = False

    def set_unexpected(self) -> None:
        self.is_abnormal = False
        self.is_unexpected = True
        self.is_foreseen = False
        self.is_next_up = False

    def set_foreseen(self) -> None:
        self.is_abnormal = False
        self.is_unexpected = False
        self.is_foreseen = True
        self.is_next_up = False

    def set_next_up(self) -> None:
        self.is_abnormal = False
        self.is_unexpected = False
        self.is_foreseen = True
        self.is_next_up = True


@dataclass
class TransitionValidatorDummy:
    is_valid: bool = False

    def validate_transition(
        self, transition: StatusTransitionProtocol, setting: ExpectednessSetting
    ) -> bool:
        return self.is_valid

    def set_valid(self) -> None:
        self.is_valid = True

    def set_invalid(self) -> None:
        self.is_valid = False


@pytest.fixture
def transition_dummy() -> TransitionDummy:
    return TransitionDummy(from_status=Status.PENDING, to_status=Status.PENDING)


@pytest.fixture
def transition_validator_dummy() -> TransitionValidatorDummy:
    return TransitionValidatorDummy()


def test_validate_transition(transition_dummy: TransitionDummy) -> None:
    E = ExpectednessSetting
    is_valid = lambda setting: _validate_transition(
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


def test_update_order_status_invalid_order_id(
    id_generator: Callable[[], Identifier],
    update_order_dummy: UpdateOrderDummy,
    get_order_by_id_dummy: GetOrderByOrderIdDummy,
    event_dispatcher_dummy: EventDispatcherDummy,
    transition_validator_dummy: TransitionValidatorDummy,
) -> None:
    # Setup:
    service = UpdateOrderStatusService(
        update_order_spi=update_order_dummy,
        get_order_by_order_id_spi=get_order_by_id_dummy,
        status_update_event_dispatcher_spi=event_dispatcher_dummy,
        _validate_transition=transition_validator_dummy.validate_transition,
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
    update_order_dummy: UpdateOrderDummy,
    get_order_by_id_dummy: GetOrderByOrderIdDummy,
    event_dispatcher_dummy: EventDispatcherDummy,
    transition_validator_dummy: TransitionValidatorDummy,
) -> None:
    # Setup:
    service = UpdateOrderStatusService(
        update_order_spi=update_order_dummy,
        get_order_by_order_id_spi=get_order_by_id_dummy,
        status_update_event_dispatcher_spi=event_dispatcher_dummy,
        _validate_transition=transition_validator_dummy.validate_transition,
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
    update_order_dummy: UpdateOrderDummy,
    get_order_by_id_dummy: GetOrderByOrderIdDummy,
    event_dispatcher_dummy: EventDispatcherDummy,
    transition_validator_dummy: TransitionValidatorDummy,
) -> None:
    # Setup:
    service = UpdateOrderStatusService(
        update_order_spi=update_order_dummy,
        get_order_by_order_id_spi=get_order_by_id_dummy,
        status_update_event_dispatcher_spi=event_dispatcher_dummy,
        _validate_transition=transition_validator_dummy.validate_transition,
    )
    get_order_by_id_dummy.orders = {persisted_order.id: persisted_order}
    transition_validator_dummy.set_valid()
    new_status = Status.ACCEPTED_BY_INVENTORY
    expected_result = persisted_order.update_status(new_status=new_status)
    expected_event_type = StatusToEventMapper.map_status_to_event(status=new_status)
    expected_event = expected_event_type(order=expected_result)

    # Run:
    result = service.update_order_status(
        order_id=persisted_order.id, new_status=new_status
    )

    # Asserts:
    assert result == expected_result
    assert update_order_dummy.read() == {persisted_order.id: new_status}
    assert event_dispatcher_dummy.read() == [expected_event]
