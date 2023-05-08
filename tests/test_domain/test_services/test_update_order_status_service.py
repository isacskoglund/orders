from domain.models.event import StatusToEventMapper, DispatchableEvent
from domain.models.identifier import Identifier
from domain.models.order import PersistedOrder
from domain.models.order_status import Status, StatusTransitionProtocol
from domain.ports.spi.order_persistence_spi import UpdateOrderSPI, GetOrderByOrderIdSPI
from domain.ports.spi.status_update_event_dispatcher_spi import (
    StatusUpdateEventDispatcherSPI,
)
from domain.ports.api.update_order_status_api import ExpectednessSetting
from domain.services.update_order_status_service import (
    UpdateOrderStatusService,
    _validate_transition,
)
from domain.errors import InvalidOrderIdError, InsufficientExpectednessError
from dataclasses import dataclass
import pytest


class UpdateOrderDummy(UpdateOrderSPI):
    statuses: dict[Identifier, Status] = {}

    def update_order_status(self, order_id: Identifier, new_status: Status) -> None:
        self.statuses[order_id] = new_status

    def reset(self) -> None:
        self.statuses = {}

    def read(self) -> tuple[Identifier, Status]:
        return self.statuses

    def is_empty(self) -> bool:
        return self.statuses == {}


class GetOrderByOrderIdDummy(GetOrderByOrderIdSPI):
    orders: dict[Identifier, PersistedOrder] = {}

    def get_order_by_order_id(self, order_id: Identifier) -> PersistedOrder | None:
        return self.orders.get(order_id)

    def reset(self) -> None:
        self.orders = {}

    def add(self, order: PersistedOrder) -> None:
        self.orders[order.id] = order


class EventDispatcherDummy(StatusUpdateEventDispatcherSPI):
    dispatched_events: list[DispatchableEvent] = []

    def dispatch_event(self, event: DispatchableEvent) -> None:
        self.dispatched_events.append(event)

    def reset(self) -> None:
        self.dispatched_events = []

    def read(self) -> list[DispatchableEvent]:
        return self.dispatched_events

    def is_empty(self) -> bool:
        return self.dispatched_events == []


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


class TestUpdateOrderStatusService:
    update_order_dummy = UpdateOrderDummy()
    get_order_dummy = GetOrderByOrderIdDummy()
    event_dispatcher_dummy = EventDispatcherDummy()
    transition_validator_dummy = TransitionValidatorDummy()
    service = UpdateOrderStatusService(
        update_order_spi=update_order_dummy,
        get_order_by_order_id_spi=get_order_dummy,
        status_update_event_dispatcher_spi=event_dispatcher_dummy,
        _validate_transition=transition_validator_dummy.validate_transition,
    )

    _status_to_event_mapper = StatusToEventMapper()
    create_expected_event = _status_to_event_mapper.create_event

    def _reset_dummies(self):
        self.update_order_dummy.reset()
        self.get_order_dummy.reset()
        self.event_dispatcher_dummy.reset()
        self.transition_validator_dummy.set_invalid()

    def test_update_order_status_invalid_order_id(self, identifier: Identifier) -> None:
        self._reset_dummies()
        with pytest.raises(InvalidOrderIdError):
            self.service.update_order_status(
                order_id=identifier, new_status=Status.ACCEPTED_BY_INVENTORY
            )

        assert self.update_order_dummy.is_empty()
        assert self.event_dispatcher_dummy.is_empty()

    def test_update_order_status_invalid_transition(
        self, persisted_order: PersistedOrder
    ) -> None:
        self._reset_dummies()
        self.get_order_dummy.add(order=persisted_order)
        self.transition_validator_dummy.set_invalid()
        with pytest.raises(InsufficientExpectednessError):
            self.service.update_order_status(
                order_id=persisted_order.id, new_status=Status.PENDING
            )

        assert self.update_order_dummy.is_empty()
        assert self.event_dispatcher_dummy.is_empty()

    def test_update_order_status_success(self, persisted_order: PersistedOrder) -> None:
        self._reset_dummies()
        self.get_order_dummy.add(order=persisted_order)
        self.transition_validator_dummy.set_valid()
        new_status = Status.ACCEPTED_BY_INVENTORY
        result = self.service.update_order_status(
            order_id=persisted_order.id, new_status=new_status
        )
        expected_result = persisted_order.update_status(new_status=new_status)
        expected_event = self.create_expected_event(order=expected_result)

        assert result == expected_result
        assert self.update_order_dummy.read() == {persisted_order.id: new_status}
        assert self.event_dispatcher_dummy.read() == [expected_event]
