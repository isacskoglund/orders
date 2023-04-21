from models.identifiers import OrderId
from models.order import PersistedOrder
from ports.spi.update_order_status_port import UpdateOrderStatusPort
from ports.spi.get_orders_port import GetOrdersPort
from internals.order_status_update_to_event_router import OrderStatusUpdateToEventRouter
from errors import UnexpectedStatusUpdateError


class UpdateOrderStatusService(UpdateOrderStatusPort):
    S = PersistedOrder.Status

    def __init__(
        self,
        get_orders_port: GetOrdersPort,
        update_order_status_port: UpdateOrderStatusPort,
        order_event_dispatcher: OrderStatusUpdateToEventRouter,
    ):
        self._get_orders = get_orders_port.get_orders_by_order_ids
        self._update_order_status = update_order_status_port.update_order_status

    def update_order_status(
        self, order_id: OrderId, new_status: S, force: bool = False
    ) -> None:
        if force:
            self._perform_update(order_id=order_id)
        order = self._get_orders(order_ids=[order_id])[0]
        update_is_unexpected = self._update_is_expected(current_status=order.status)
        if update_is_unexpected:
            raise UnexpectedStatusUpdateError
        self._perform_update(order_id=order_id)

    def _update_is_unexpected(
        self, current_status: PersistedOrder.Status, new_status: PersistedOrder.Status
    ) -> bool:
        new_status_is_next = current_status.value != new_status.value - 1
        return new_status_is_next

    def _perform_update(self, order_id: OrderId, new_status: S) -> None:
        self._update_order_status(order_id=order_id, new_status=new_status)
