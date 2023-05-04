from domain.models.identifier import Identifier
from domain.ports.api.update_order_status_api import UpdateOrderStatusAPI
from domain.ports.spi.order_persistence_spi import UpdateOrderSPI, GetOrderByOrderIdSPI
from domain.ports.spi.status_update_event_dispatcher_spi import (
    StatusUpdateEventDispatcherSPI,
)

from domain.models.order import PersistedOrder
from domain.models.order_status import Status, StatusTransition
from domain.models.event import StatusToEventMapper
from domain.errors import InvalidOrderIdError, UnexpectedStatusUpdateError


class UpdateOrderStatusService(UpdateOrderStatusAPI):
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
        self, order_id: Identifier, new_status: Status, force: bool = False
    ) -> PersistedOrder:
        order = self._get_order(order_id=order_id)
        if order is None:
            raise InvalidOrderIdError(order_id=order_id)
        status_transition = StatusTransition(
            from_status=order.status, to_status=new_status
        )
        update_should_be_performed = not status_transition.is_abnormal or force
        if not update_should_be_performed:
            raise UnexpectedStatusUpdateError(order_id=order_id)
        updated_order = self._perform_update(order=order, new_status=new_status)
        return updated_order

    def _perform_update(
        self, order: PersistedOrder, new_status: Status
    ) -> PersistedOrder:
        self._save_new_status(order_id=order.id, new_status=new_status)
        updated_order = order.update_status(new_status=new_status)
        event = self._create_event(order=updated_order)
        if event is not None:
            self._dispatch_event(event=event)
        return updated_order
