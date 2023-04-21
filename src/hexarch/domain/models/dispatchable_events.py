from dataclasses import dataclass
from order import PersistedOrder
from identifiers import OrderId


@dataclass
class DispatchableEvent:
    needs_order: bool  # CONVENTION: If false, then needs `order_id`


@dataclass
class OrderCreatedEvent(DispatchableEvent):
    needs_order = True
    order: PersistedOrder


@dataclass
class OrderAcceptedByInventoryEvent(DispatchableEvent):
    needs_order = True
    order: PersistedOrder


@dataclass
class OrderPaidEvent(DispatchableEvent):
    needs_order = True
    order: PersistedOrder


@dataclass
class OrderShippedEvent(DispatchableEvent):
    needs_order = False
    order_id: OrderId


@dataclass
class OrderCancelledEvent(DispatchableEvent):
    needs_order = False
    order_id: OrderId
