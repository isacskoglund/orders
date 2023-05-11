from dataclasses import dataclass
from typing import Protocol
from .order import PersistedOrder
from .order_status import Status
from domain.utils.singleton_meta import SingletonMeta
from enum import Enum, auto


@dataclass
class DispatchableEvent:
    class EventType(Enum):
        TO_BE_ACCEPTED_BY_INVENTORY = auto()
        TO_BE_PAID = auto()
        TO_BE_SHIPPED = auto()
        SHIPPED = auto()
        CANCELLED = auto()

    order: PersistedOrder
    event_type: EventType


class StatusToEventMapperProtocol(Protocol):
    def map_status_to_event_type(
        self, status: Status
    ) -> DispatchableEvent.EventType | None:
        ...


class StatusToEventMapper(metaclass=SingletonMeta):
    T = DispatchableEvent.EventType
    status_to_event_type_map = {
        Status.PENDING: T.TO_BE_ACCEPTED_BY_INVENTORY,
        Status.ACCEPTED_BY_INVENTORY: T.TO_BE_PAID,
        Status.PAID: T.TO_BE_SHIPPED,
        Status.SHIPPED: T.SHIPPED,
        Status.CANCELLED: T.CANCELLED,
    }

    @classmethod
    def map_status_to_event_type(
        cls, status: Status
    ) -> DispatchableEvent.EventType | None:
        if status not in cls.status_to_event_type_map:
            return None
        return cls.status_to_event_type_map[status]
