from typing import Protocol
from domain.models.order import VersionedOrder, PersistedOrder
from domain.models.identifier import Identifier
from domain.models.order_status import Status


class GetOrderByOrderIdSPI(Protocol):
    def get_order_by_order_id(self, order_id: Identifier) -> PersistedOrder | None:
        ...


class GetOrdersByCustomerIdSPI(Protocol):
    def get_orders_by_customer_id(
        self, customer_id: Identifier
    ) -> list[PersistedOrder]:
        ...


class SaveOrderSPI(Protocol):
    def save_order(self, versioned_order: VersionedOrder) -> PersistedOrder:
        """
        Raises:
            SaveOrderError
        """
        ...


class UpdateOrderSPI(Protocol):
    def update_order_status(self, order_id: Identifier, new_status: Status) -> None:
        """
        Raises:
            UpdateOrderError
        """
        ...
