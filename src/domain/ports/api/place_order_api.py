from abc import ABC, abstractmethod
from domain.models.order import RequestedOrder, PersistedOrder


class PlaceOrderAPI(ABC):
    @abstractmethod
    def place_order(self, requested_order: RequestedOrder) -> PersistedOrder:
        """
        Raises:
           InvalidProductIdError
           NoCurrentProductVersionError
        """
