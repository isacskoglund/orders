from typing import Protocol
from dataclasses import dataclass
from models.identifiers import OrderId
from models.order import OrderStatus


class UpdateOrderStatusUseCase(Protocol):
    # Result
    @dataclass(frozen=True)
    class UpdateOrderStatusResult:
        pass

    class OrderNotFoundByIdResult(UpdateOrderStatusResult):
        pass

    class InvalidOrderStatus(UpdateOrderStatusResult):
        pass

    # Use Case

    def update_order_status(
        self, order_id: OrderId, new_status: OrderStatus
    ) -> UpdateOrderStatusResult:
        raise NotImplementedError
