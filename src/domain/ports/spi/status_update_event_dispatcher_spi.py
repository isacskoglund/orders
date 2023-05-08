from typing import Protocol
import domain.models.event as event

Events = (
    event.OrderToBeAcceptedByInventoryEvent
    | event.OrderToBePaidEvent
    | event.OrderToBeShippedEvent
    | event.OrderShippedEvent
    | event.OrderCancelledEvent
)


class StatusUpdateEventDispatcherSPI(Protocol):
    def dispatch_event(self, event: Events) -> None:
        raise NotImplementedError
