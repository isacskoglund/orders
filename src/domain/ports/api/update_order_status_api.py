from typing import Protocol
from domain.models.identifier import Identifier
from domain.models.order import PersistedOrder


class UpdateOrderStatusAPI(Protocol):
    S = PersistedOrder.Status

    def update_order_status(
        order_id: Identifier, new_status: S, force: bool = False
    ) -> None:
        """
        Raises:
           InvalidOrderIdError
           UnexpectedStatusUpdateError
        """
        raise NotImplementedError
