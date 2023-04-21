from typing import Protocol
from models.identifiers import OrderId


class CancelOrderUseCase(Protocol):
    def cancel_order(self, order_id: OrderId, force: bool = False) -> None:
        """
        Raises:
            InvalidOrderIdError: Order was not found.
            NoLongerCancelableError:
                The order can no longer be canceled.
                Can be overridden with `force=True`.
        """
        raise NotImplementedError
