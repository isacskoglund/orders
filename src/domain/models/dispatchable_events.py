from dataclasses import dataclass
from .order import PersistedOrder


@dataclass
class DispatchableEvent:
    order: PersistedOrder


@dataclass
class OrderToBeValidated(DispatchableEvent):
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


class StatusToDispatchableEventMapper:
    S = PersistedOrder.Status
    status_to_dispatchable_event_map = {
        S.REQUESTED: OrderToBeValidated,
        S.VALIDATED: OrderToBePaidEvent,
        S.PAID: OrderToBeShippedEvent,
        S.SHIPPED: OrderShippedEvent,
        S.CANCELLED: OrderCancelledEvent,
    }

    def map_status_to_event(self, status: PersistedOrder.Status) -> type[DispatchableEvent] | None:
        if status not in self.status_to_dispatchable_event_map:
            return None
        return self.status_to_dispatchable_event_map[status]

    def create_event(self, order: PersistedOrder) -> DispatchableEvent | None:
        status = order.status
        event_cls = self.map_status_to_event(status=status)
        if event_cls is None:
            return None
        return event_cls(order=order)
