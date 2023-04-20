from ports.api.place_order_use_case import PlaceOrderUseCase

from ports.spi.assign_product_versions_port import AssignProductVersionsPort
from ports.spi.persist_order_port import PersistOrderPort
from ports.spi.dispatch_order_status_update_event_port import (
    DispatchOrderStatusUpdateEventPort,
)

from models.order import RequestedOrder, PersistedOrder


class OrdersService(PlaceOrderUseCase):
    def __init__(
        self,
        assign_product_versions_port: AssignProductVersionsPort,
        persist_order_port: PersistOrderPort,
        dispatch_order_status_update_event_port: DispatchOrderStatusUpdateEventPort,
    ) -> None:
        self._assign_product_versions = (
            assign_product_versions_port.assign_product_versions
        )
        self._persist_order = persist_order_port.persist_order
        self._dispatch_order_status_update_event = (
            dispatch_order_status_update_event_port.dispatch_order_status_update_event
        )

    def place_order(self, requested_order: RequestedOrder) -> PersistedOrder:
        versioned_order = self._assign_product_versions(requested_order=requested_order)
        persisted_order = self._persist_order(versioned_order=versioned_order)
        self._dispatch_order_status_update_event(persisted_order)
        return PersistedOrder

    # ToDo: Add order cancellation.
