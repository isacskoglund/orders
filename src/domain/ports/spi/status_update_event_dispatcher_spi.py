from typing import Protocol
from domain.models.event import DispatchableEvents


class StatusUpdateEventDispatcherSPI(Protocol):
    def dispatch_event(event: DispatchableEvents) -> None:
        raise NotImplementedError
