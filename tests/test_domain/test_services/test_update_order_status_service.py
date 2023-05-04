from domain.models.event import StatusToEventMapper, DispatchableEvents
from domain.models.identifier import Identifier
from domain.models.order import PersistedOrder
from domain.models.order_status import Status
from domain.ports.spi.order_persistence_spi import UpdateOrderSPI, GetOrderByOrderIdSPI
from domain.ports.spi.status_update_event_dispatcher_spi import (
    StatusUpdateEventDispatcherSPI,
)
from domain.services.update_order_status_service import UpdateOrderStatusService
from domain.errors import InvalidOrderIdError, UnexpectedStatusUpdateError
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
    dispatched_events: list[DispatchableEvents] = []

    def dispatch_event(self, event: DispatchableEvents) -> None:
        self.dispatched_events.append(event)

    def reset(self) -> None:
        self.dispatched_events = []

    def read(self) -> list[DispatchableEvents]:
        return self.dispatched_events

    def is_empty(self) -> bool:
        return self.dispatched_events == []


class TestUpdateOrderStatusService:
    update_order_dummy = UpdateOrderDummy()
    get_order_dummy = GetOrderByOrderIdDummy()
    event_dispatcher_dummy = EventDispatcherDummy()
    service = UpdateOrderStatusService(
        update_order_spi=update_order_dummy,
        get_order_by_order_id_spi=get_order_dummy,
        status_update_event_dispatcher_spi=event_dispatcher_dummy,
    )

    _status_to_event_mapper = StatusToEventMapper()
    create_expected_event = _status_to_event_mapper.create_event

    def _reset_dummies(self):
        self.update_order_dummy.reset()
        self.get_order_dummy.reset()
        self.event_dispatcher_dummy.reset()

    def test_update_order_invalid_id(self, identifier: Identifier) -> None:
        self._reset_dummies()
        with pytest.raises(InvalidOrderIdError):
            self.service.update_order_status(
                order_id=identifier, new_status=Status.ACCEPTED_BY_INVENTORY
            )

        assert self.update_order_dummy.is_empty()
        assert self.event_dispatcher_dummy.is_empty()

    def test_update_order_status_unexpected(
        self, persisted_order: PersistedOrder
    ) -> None:
        self._reset_dummies()
        self.get_order_dummy.add(order=persisted_order)
        with pytest.raises(UnexpectedStatusUpdateError):
            self.service.update_order_status(
                order_id=persisted_order.id, new_status=Status.PENDING
            )

        assert self.update_order_dummy.is_empty()
        assert self.event_dispatcher_dummy.is_empty()

    def test_update_order_status_without_force(
        self, persisted_order: PersistedOrder
    ) -> None:
        self._reset_dummies()
        self.get_order_dummy.add(order=persisted_order)
        new_status = Status.ACCEPTED_BY_INVENTORY
        result = self.service.update_order_status(
            order_id=persisted_order.id, new_status=new_status
        )
        expected_result = persisted_order.update_status(new_status=new_status)
        expected_event = self.create_expected_event(order=expected_result)

        assert result == expected_result
        assert self.update_order_dummy.read() == {persisted_order.id: new_status}
        assert self.event_dispatcher_dummy.read() == [expected_event]
