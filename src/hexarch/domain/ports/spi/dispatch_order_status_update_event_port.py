from typing import Protocol
from models.order import PersistedOrder


class DispatchOrderStatusUpdateEventPort(Protocol):
    def dispatch_order_status_update_event(self, order: PersistedOrder) -> None:
        pass
