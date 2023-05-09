from dataclasses import dataclass
from typing import Protocol
from .order import PersistedOrder
from .order_status import Status
from domain.utils.singleton_meta import SingletonMeta


@dataclass
class DispatchableEvent:
    order: PersistedOrder


@dataclass
class OrderToBeAcceptedByInventoryEvent(DispatchableEvent):
    pass


@dataclass
class OrderToBePaidEvent(DispatchableEvent):
    pass


@dataclass
class OrderToBeShippedEvent(DispatchableEvent):
    pass


@dataclass
class OrderShippedEvent(DispatchableEvent):
    pass


@dataclass
class OrderCancelledEvent(DispatchableEvent):
    pass


class StatusToEventMapperProtocol(Protocol):
    def map_status_to_event(self, status: Status) -> type[DispatchableEvent] | None:
        ...


class StatusToEventMapper(metaclass=SingletonMeta):
    status_to_event_map = {
        Status.PENDING: OrderToBeAcceptedByInventoryEvent,
        Status.ACCEPTED_BY_INVENTORY: OrderToBePaidEvent,
        Status.PAID: OrderToBeShippedEvent,
        Status.SHIPPED: OrderShippedEvent,
        Status.CANCELLED: OrderCancelledEvent,
    }

    def map_status_to_event(self, status: Status) -> type[DispatchableEvent] | None:
        if status not in self.status_to_event_map:
            return None
        return self.status_to_event_map[status]

    def create_event(self, order: PersistedOrder) -> DispatchableEvent | None:
        status = order.status
        event_cls = self.map_status_to_event(status=status)
        if event_cls is None:
            return None
        return event_cls(order=order)
