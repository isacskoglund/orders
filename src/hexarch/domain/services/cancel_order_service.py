from ports.api.cancel_order_use_case import CancelOrderUseCase

from ports.spi.update_order_status_port import UpdateOrderStatusPort
from ports.spi.dispatch_order_status_update_event_port import (
    DispatchOrderStatusUpdateEventPort,
)
from ports.spi.get_orders_port import GetOrdersPort

from models.identifiers import OrderId
from models.order import PersistedOrder
from errors import NoLongerCancelableError


class CancelOrderService(CancelOrderUseCase):
    ORDER_CANCELLATION_MUST_BE_FORCED_STATUS = (
        PersistedOrder.Status.NO_LONGER_CANCELABLE
    )

    def __init__(
        self,
        update_order_status_port: UpdateOrderStatusPort,
        dispatch_order_status_update_event_port: DispatchOrderStatusUpdateEventPort,
        get_orders_port: GetOrdersPort,
    ) -> None:
        self._update_order_status = update_order_status_port.update_order_status
        self._dispatch_order_status_update_event = (
            dispatch_order_status_update_event_port.dispatch_order_status_update_event
        )
        self._get_orders_by_order_ids = get_orders_port.get_orders_by_order_ids

    def cancel_order(self, order_id: OrderId, force: bool = False) -> None:
        order = self._get_orders_by_order_ids(order_ids=[order_id])[0]
        if not force:
            current_status = order.status
            must_be_forced = (
                current_status >= self.ORDER_CANCELLATION_MUST_BE_FORCED_STATUS
            )
        cancellation_should_be_performed = force or not must_be_forced

        if cancellation_should_be_performed:
            self._perform_order_cancellation(order=order)
            return
        raise NoLongerCancelableError(order_id=order.id)

    def _perform_order_cancellation(self, order: PersistedOrder) -> None:
        self._update_order_status(
            order_id=order.id, new_status=PersistedOrder.Status.CANCELLED
        )
        self._dispatch_order_status_update_event(order=order)
