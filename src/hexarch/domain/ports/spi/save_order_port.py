from typing import Protocol
from dataclasses import dataclass
from models.identifiers import OrderId
from models.order import Order, OrderPreSave


class SaveOrderPort(Protocol):
    # Results
    @dataclass(frozen=True)
    class SaveOrderResult:
        pass

    class FailedToSaveOrder(SaveOrderResult):
        pass

    class SuccessfullySavedOrder(SaveOrderResult):
        order: Order

    # Port
    def save_order(self, order_pre_save: OrderPreSave) -> SaveOrderResult:
        raise NotImplementedError
