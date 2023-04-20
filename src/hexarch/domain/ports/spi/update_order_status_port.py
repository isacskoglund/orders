from typing import Protocol
from models.identifiers import OrderId
from models.order import PersistedOrder


class UpdateOrderStatusPort(Protocol):
    def update_order_status(
        self, order_id: OrderId, new_status: PersistedOrder.Status
    ) -> None:
        """
        Raises:
            InvalidOrderIdError: Order was not found.
        """
        raise NotImplementedError
