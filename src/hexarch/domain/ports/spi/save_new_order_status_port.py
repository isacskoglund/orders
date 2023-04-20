from typing import Protocol
from dataclasses import dataclass
from models.identifiers import OrderId
from models.order import Order, OrderStatus


class SaveNewOrderStatusPort(Protocol):
    # Result:
    @dataclass
    class SaveNewOrderStatusResult:
        pass

    class OrderIdNotFoundResult(SaveNewOrderStatusResult):
        pass

    class SuccessfullySavedNewOrderStatusResult(SaveNewOrderStatusResult):
        new_order: Order

    # Port:
    def save_new_order_status(
        self, order_id: OrderId, new_status: OrderStatus
    ) -> SaveNewOrderStatusResult:
        raise NotImplementedError
