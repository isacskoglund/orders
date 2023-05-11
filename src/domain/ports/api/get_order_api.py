from abc import ABC, abstractmethod
from domain.models.identifier import Identifier
from domain.models.order import PersistedOrder


class GetOrderByOrderIdAPI(ABC):
    @abstractmethod
    def get_order_by_order_id(self, order_id: Identifier) -> PersistedOrder:
        """
        Raises:
            InvalidOrderIdError
            ReadFromPersistenceError
        """
        ...


class GetOrderByCustomerIdAPI(ABC):
    @abstractmethod
    def get_order_by_customer_id(self, customer_id: Identifier) -> list[PersistedOrder]:
        """
        Raises:
            ReadFromPersistenceError
        """
        ...
