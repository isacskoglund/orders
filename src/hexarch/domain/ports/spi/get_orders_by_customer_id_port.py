from typing import Protocol
from dataclasses import dataclass
from models.identifiers import CustomerId
from models.order import Order


class GetOrdersByCustomerIdPort(Protocol):
    # Results:

    @dataclass(frozen=True)
    class GetOrdersByCustomerIdResult:
        pass

    class CustomerNotFoundResult(GetOrdersByCustomerIdResult):
        pass

    class SuccessfullyFoundOrdersByCustomerIdResult(GetOrdersByCustomerIdResult):
        orders: list[Order]

    # Port:

    def get_orders_by_customer_id(
        self, customer_id: CustomerId
    ) -> GetOrdersByCustomerIdResult:
        raise NotImplementedError
