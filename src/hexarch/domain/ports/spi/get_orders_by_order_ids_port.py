from typing import Protocol
from dataclasses import dataclass
from models.identifiers import OrderId
from models.order import Order


class GetOrdersByOrderIdsPort(Protocol):
    # Results:

    @dataclass(frozen=True)
    class GetOrdersByOrderIdsResult:
        pass

    class OrdersNotFoundResult(GetOrdersByOrderIdsResult):
        order_ids_not_found: list[OrderId]

    class SuccessfullyGotOrdersByIdResult(GetOrdersByOrderIdsResult):
        orders: list[Order]

    # Port:

    def get_orders_by_order_ids(
        self, order_ids: list[OrderId]
    ) -> GetOrdersByOrderIdsResult:
        raise NotImplementedError
