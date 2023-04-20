from typing import Protocol
from dataclasses import dataclass
from models.order import Order, OrderStatus


class DispatchOrderUpdateMessagePort(Protocol):
    # Message
    @dataclass
    class OrderUpdateMessage:
        order: Order

    # Results:
    @dataclass
    class DispatchOrdersMessageResult:
        pass

    class SuccessfullyDispatchedMessage(DispatchOrdersMessageResult):
        pass

    # Port
    def dispatch_order_update_message(
        self, message: OrderUpdateMessage
    ) -> DispatchOrdersMessageResult:
        raise NotImplementedError
