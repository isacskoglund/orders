from typing import Protocol
from domain.models.identifier import Identifier
from domain.models.order import PersistedOrder
from domain.models.order_status import Status


class UpdateOrderStatusAPI(Protocol):
    
    def update_order_status(
        self, order_id: Identifier, new_status: Status, force: bool = False
    ) -> PersistedOrder:
        """
        Raises:
           InvalidOrderIdError
           UnexpectedStatusUpdateError
        """
        raise NotImplementedError
