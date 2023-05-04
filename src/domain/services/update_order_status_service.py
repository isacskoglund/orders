from domain.models.identifier import Identifier
from domain.ports.api.update_order_status_api import UpdateOrderStatusAPI
from domain.ports.spi.order_persistence_spi import UpdateOrderSPI, GetOrderByOrderIdSPI
from domain.ports.spi.status_update_event_dispatcher_spi import (
    StatusUpdateEventDispatcherSPI,
)

from domain.models.order import PersistedOrder
from domain.models.event import StatusToEventMapper
from domain.errors import InvalidOrderIdError, UnexpectedStatusUpdateError


class UpdateOrderStatusService(UpdateOrderStatusAPI):
    S = PersistedOrder.Status

    def __init__(
        self,
        update_order_spi: UpdateOrderSPI,
        get_order_by_order_id_spi: GetOrderByOrderIdSPI,
        status_update_event_dispatcher_spi: StatusUpdateEventDispatcherSPI,
    ) -> None:
        self._save_new_status = update_order_spi.update_order_status
        self._get_order = get_order_by_order_id_spi.get_order_by_order_id
        self._dispatch_event = status_update_event_dispatcher_spi.dispatch_event

        event_mapper = StatusToEventMapper()
        self._create_event = event_mapper.create_event

    def update_order_status(
        self, order_id: Identifier, new_status: S, force: bool = False
    ) -> PersistedOrder:
        order = self._get_order(order_id=order_id)
        if order is None:
            raise InvalidOrderIdError(order_id=order_id)
        if new_status == order.status:
            return
        update_is_expected = self._update_is_expected(
            current_status=order.status, new_status=new_status
        )
        update_should_be_performed = update_is_expected or force
        if not update_should_be_performed:
            raise UnexpectedStatusUpdateError(order_id=order_id)
        updated_order = self._perform_update(order=order, new_status=new_status)
        return updated_order

    @staticmethod
    def _update_is_expected(current_status: S, new_status: S) -> bool:
        return current_status.value == new_status.value - 1

    def _perform_update(self, order: PersistedOrder, new_status: S) -> PersistedOrder:
        self._save_new_status(order_id=order.id, new_status=new_status)
        updated_order = order.update_status(new_status=new_status)
        event = self._create_event(order=updated_order)
        if event is not None:
            self._dispatch_event(event=event)
        return updated_order
