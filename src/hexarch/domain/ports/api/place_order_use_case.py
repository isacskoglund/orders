from typing import Protocol
from models.order import RequestedOrder, PersistedOrder


class PlaceOrderUseCase(Protocol):
    def place_order(self, requested_order: RequestedOrder) -> PersistedOrder:
        """
        Raises:
            InvalidProductIdError: Product was not found.
            NoCurrentProductVersion: Product has no current version.
        """
        raise NotImplementedError
