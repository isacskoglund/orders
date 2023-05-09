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

    @classmethod
    def map_status_to_event(cls, status: Status) -> type[DispatchableEvent] | None:
        if status not in cls.status_to_event_map:
            return None
        return cls.status_to_event_map[status]
