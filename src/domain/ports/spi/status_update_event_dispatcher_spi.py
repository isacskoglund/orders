from typing import Protocol
from domain.models.event import DispatchableEvents


class StatusUpdateEventDispatcherSPI(Protocol):
    def dispatch_event(self, event: DispatchableEvents) -> None:
        raise NotImplementedError
