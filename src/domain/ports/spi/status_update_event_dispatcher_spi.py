from typing import Protocol
from domain.models.event import DispatchableEvent


class StatusUpdateEventDispatcherSPI(Protocol):
    def dispatch_event(self, event: DispatchableEvent) -> None:
        ...
