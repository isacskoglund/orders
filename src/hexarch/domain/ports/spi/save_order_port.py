from typing import Protocol
from dataclasses import dataclass
from models.identifiers import OrderId
from models.order import Order


class SaveOrderPort(Protocol):
    # Results
    @dataclass(frozen=True)
    class AddOrderResult:
        pass

    class FailedToSaveOrder(AddOrderResult):
        pass

    class SuccessfullyAddedOrder(AddOrderResult):
        order_id: OrderId

    # Port
    def save_order(self, order: Order):
        raise NotImplementedError
