from typing import Protocol
from models.identifiers import CustomerId, OrderId
from models.order import PersistedOrder


class GetOrdersPort(Protocol):
    def get_orders_by_customer_id(
        self, customer_id: CustomerId
    ) -> list[PersistedOrder]:
        """
        Raises:
            InvalidCustomerIdError: Customer was not found.
        """
        raise NotImplementedError

    def get_orders_by_order_ids(self, order_ids: list[OrderId]) -> list[PersistedOrder]:
        """
        Raises:
            InvalidOrderIdError: Order was not found.
        """
        raise NotImplementedError
