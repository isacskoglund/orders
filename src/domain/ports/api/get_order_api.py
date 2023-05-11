from abc import ABC, abstractmethod
from domain.models.identifier import Identifier
from domain.models.order import OrderData


class GetOrderDataByOrderIdAPI(ABC):
    @abstractmethod
    def get_order_by_order_id(self, order_id: Identifier) -> OrderData:
        """
        Raises:
            InvalidOrderIdError
            ReadFromPersistenceError
        """
        ...


class GetOrderDataByCustomerIdAPI(ABC):
    @abstractmethod
    def get_order_by_customer_id(self, customer_id: Identifier) -> list[OrderData]:
        """
        Raises:
            ReadFromPersistenceError
        """
        ...
