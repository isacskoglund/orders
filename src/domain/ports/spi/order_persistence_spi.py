from typing import Protocol
from domain.models.order import VersionedOrder, PersistedOrder
from domain.models.identifier import Identifier


class OrderPersistenceSPI(Protocol):
    def get_orders_by_order_ids(
        self, order_ids: list[Identifier]
    ) -> list[PersistedOrder]:
        raise NotImplementedError

    def get_orders_by_customer_id(
        self, customer_id: Identifier
    ) -> list[PersistedOrder]:
        raise NotImplementedError

    def save_order(self, versioned_order: VersionedOrder) -> PersistedOrder:
        raise NotImplementedError

    def update_order_status(
        self, order_id: Identifier, new_status: PersistedOrder.Status
    ) -> None:
        raise NotImplementedError
