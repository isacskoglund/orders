from typing import Protocol
from dataclasses import dataclass
from models.identifiers import OrderId
from models.order import Order

# Results


@dataclass(frozen=True)
class GetOrdersByOrderIdsResult:
    pass


class OrdersNotFoundResult(GetOrdersByOrderIdsResult):
    orders_not_found_ids: list[OrderId]


class SuccessfullyGotOrdersByIdResult(GetOrdersByOrderIdsResult):
    orders: list[Order]


# Use Case


class GetOrdersByOrderIdsUseCase(Protocol):
    def get_orders_by_order_ids(
        self, order_ids: list[OrderId]
    ) -> GetOrdersByOrderIdsResult:
        raise NotImplementedError
