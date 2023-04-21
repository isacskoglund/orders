from typing import Protocol
from models.dispatchable_events import DispatchableEvent


class EventDispatcherPort(Protocol):
    def dispatch_event(self, dispatchable_event: DispatchableEvent) -> None:
        raise NotImplementedError
