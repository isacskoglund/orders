from typing import Protocol
from domain.models.identifier import Identifier
from domain.models.order import PersistedOrder


class UpdateOrderStatusAPI(Protocol):
    S = PersistedOrder.Status

    def update_order_status(
        self, order_id: Identifier, new_status: S, force: bool = False
    ) -> PersistedOrder:
        """
        Raises:
           InvalidOrderIdError
           UnexpectedStatusUpdateError
        """
        raise NotImplementedError
