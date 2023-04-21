from typing import Protocol
from models.identifiers import OrderId
from models.order import PersistedOrder


class UpdateOrderStatusUseCase(Protocol):
    def update_order_status(
        order_id: OrderId, new_status: PersistedOrder.Status, force: bool = False
    ):
        raise NotImplementedError
