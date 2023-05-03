from typing import Protocol
from domain.models.order import VersionedOrder, PersistedOrder
from domain.models.identifier import Identifier


class GetOrderSPI(Protocol):
    def get_order_by_order_id(self, order_id: Identifier) -> PersistedOrder:
        raise NotImplementedError

    def get_orders_by_customer_id(
        self, customer_id: Identifier
    ) -> list[PersistedOrder]:
        raise NotImplementedError


class SaveOrderSPI(Protocol):
    def save_order(self, versioned_order: VersionedOrder) -> PersistedOrder:
        raise NotImplementedError


class UpdateOrderSPI(Protocol):
    def update_order_status(
        self, order_id: Identifier, new_status: PersistedOrder.Status
    ) -> None:
        raise NotImplementedError
