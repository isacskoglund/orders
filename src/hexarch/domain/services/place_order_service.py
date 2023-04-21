from ports.api.place_order_use_case import PlaceOrderUseCase

from ports.spi.get_current_product_versions_port import GetCurrentProductVersionsPort
from ports.spi.persist_order_port import PersistOrderPort
from ports.spi.dispatch_order_status_update_event_port import (
    DispatchOrderStatusUpdateEventPort,
)

from models.order import RequestedOrder, PersistedOrder


class PlaceOrderService(PlaceOrderUseCase):
    def __init__(
        self,
        get_current_product_versions_port: GetCurrentProductVersionsPort,
        persist_order_port: PersistOrderPort,
        dispatch_order_status_update_event_port: DispatchOrderStatusUpdateEventPort,
    ) -> None:
        self._get_current_product_versions = (
            get_current_product_versions_port.get_current_product_versions
        )
        self._persist_order = persist_order_port.persist_order
        self._dispatch_order_status_update_event = (
            dispatch_order_status_update_event_port.dispatch_order_status_update_event
        )

    def place_order(self, requested_order: RequestedOrder) -> PersistedOrder:
        product_ids = requested_order.get_product_ids()
        product_versions = self._get_current_product_versions(product_ids=product_ids)
        versioned_order = requested_order.to_versioned_order(
            product_versions=product_versions
        )
        persisted_order = self._persist_order(versioned_order=versioned_order)
        self._dispatch_order_status_update_event(persisted_order)
        return PersistedOrder

    # ToDo: Add order cancellation.
