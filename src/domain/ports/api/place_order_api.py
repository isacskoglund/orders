from typing import Protocol
from domain.models.order import RequestedOrder, PersistedOrder


class PlaceOrderAPI(Protocol):
    def place_order(requested_order=RequestedOrder) -> PersistedOrder:
        """
        Raises:
           InvalidProductIdError
           NoCurrentProductVersionError
        """

        raise NotImplementedError
