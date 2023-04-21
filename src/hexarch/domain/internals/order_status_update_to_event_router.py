from __future__ import annotations
from typing import Protocol
from dataclasses import dataclass
from ports.spi.event_dispatcher_port import (
    EventDispatcherPort,
)
from ports.spi.get_orders_port import GetOrdersPort
from models.order import PersistedOrder
from models.identifiers import OrderId
from models.dispatchable_events import (
    DispatchableEvent,
    OrderCreatedEvent,
    OrderAcceptedByInventoryEvent,
    OrderPaidEvent,
    OrderShippedEvent,
    OrderCancelledEvent,
)


class OrderStatusUpdateToEventRouter:
    # Arguments:

    @dataclass
    class ArgWithOrder:
        order = PersistedOrder

    @dataclass
    class ArgWithoutOrder:
        order_id: OrderId
        new_status: PersistedOrder.Status

    S = PersistedOrder.Status
    status_to_event_map = {
        S.WAITING_FOR_INVENTORY: OrderCreatedEvent,
        S.ACCEPTED_BY_INVENTORY: OrderAcceptedByInventoryEvent,
        S.PAID: OrderPaidEvent,
        S.SHIPPED: OrderShippedEvent,
        S.CANCELLED: OrderCancelledEvent,
    }

    def __init__(
        self,
        order_status_update_event_dispatcher_port: EventDispatcherPort,
        get_orders_port: GetOrdersPort,
    ) -> None:
        self._dispatch_event = order_status_update_event_dispatcher_port.dispatch_event
        self._get_orders = get_orders_port.get_orders_by_order_ids

    def route(self, arg: ArgWithOrder | ArgWithoutOrder) -> DispatchableEvent | None:
        if isinstance(arg, OrderStatusUpdateToEventRouter.ArgWithOrder):
            order = arg.order
            order_id = order.id
            new_status = order.status
        else:
            order = None
            order_id = arg.order_id
            new_status = arg.new_status
        if new_status not in self.status_to_event_map:
            return None
        event_cls: DispatchableEvent = self.status_to_event_map[new_status]
        if event_cls.needs_order:
            if order is None:
                order = self._get_orders(order_ids=[order_id])[0]
            return event_cls(order=order)
        return event_cls(order_id=order_id)

    def route_and_dispatch(self, arg: ArgWithOrder | ArgWithoutOrder) -> None:
        event_result = self.route(arg=arg)
        if event_result is None:
            return
        self._dispatch_event(dispatchable_event=event_result)
