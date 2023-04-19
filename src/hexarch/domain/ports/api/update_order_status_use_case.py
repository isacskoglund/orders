from typing import Protocol
from dataclasses import dataclass
from models.identifiers import OrderId

# Result


@dataclass(frozen=True)
class UpdateOrderStatusResult:
    pass


class OrderNotFoundByIdResult(UpdateOrderStatusResult):
    pass


class InvalidOrderStatus(UpdateOrderStatusResult):
    pass


# Use Case


class UpdateOrderStatusUseCase(Protocol):
    def update_order_status(self, order_id: OrderId) -> UpdateOrderStatusResult:
        raise NotImplementedError
