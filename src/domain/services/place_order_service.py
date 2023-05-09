from domain.models.order import PersistedOrder, VersionedOrder, RequestedOrder
from domain.models.event import StatusToEventMapper
from domain.ports.api.place_order_api import PlaceOrderAPI
from domain.ports.spi.product_catalogue_spi import GetProductVersionIdsSPI
from domain.ports.spi.order_persistence_spi import SaveOrderSPI
from domain.ports.spi.status_update_event_dispatcher_spi import (
    StatusUpdateEventDispatcherSPI,
)
from domain.errors import InvalidProductIdError, NoCurrentProductVersionError
from dataclasses import dataclass


@dataclass
class PlaceOrderService(PlaceOrderAPI):
    get_product_version_ids_spi: GetProductVersionIdsSPI
    save_order_spi: SaveOrderSPI
    event_dispatcher: StatusUpdateEventDispatcherSPI

    _event_mapper = StatusToEventMapper()
    _create_event = _event_mapper.create_event

    def place_order(self, requested_order: RequestedOrder) -> PersistedOrder:
        versioned_order = self._version_order(requested_order=requested_order)
        persisted_order = self.save_order_spi.save_order(
            versioned_order=versioned_order
        )
        event = self._create_event(order=persisted_order)
        if event is not None:
            self.event_dispatcher.dispatch_event(event=event)
        return persisted_order

    def _version_order(self, requested_order: RequestedOrder) -> VersionedOrder:
        product_ids = requested_order.get_product_ids()
        get_result = self.get_product_version_ids_spi.get_product_versions(
            product_ids=product_ids
        )

        if get_result.invalid_ids != set():
            raise InvalidProductIdError(product_id=list(get_result.invalid_ids)[0])
        if get_result.ids_without_product_version_id != set():
            raise NoCurrentProductVersionError(
                product_id=list(get_result.ids_without_product_version_id)[0]
            )

        return requested_order.to_versioned_order(
            product_versions=get_result.product_version_ids
        )
