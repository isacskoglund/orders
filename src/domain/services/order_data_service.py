from domain.models.identifier import Identifier
from domain.models.order import OrderData
from domain.ports.api.get_order_api import (
    GetOrderDataByOrderIdAPI,
    GetOrderDataByCustomerIdAPI,
)
from domain.ports.spi.order_persistence_spi import (
    GetOrderDataByOrderIdSPI,
    GetOrderDataByCustomerIdSPI,
)
from domain.errors import InvalidOrderIdError


class OrderDataByOrderIdService(GetOrderDataByOrderIdAPI):
    def __init__(self, order_data_spi: GetOrderDataByOrderIdSPI) -> None:
        self._order_data_spi = order_data_spi

    def get_order_by_order_id(self, order_id: Identifier) -> OrderData:
        result = self._order_data_spi.get_order_data_by_order_id(order_id=order_id)
        if result is None:
            raise InvalidOrderIdError(order_id=order_id)
        return result


class OrderDataByCustomerIdService(GetOrderDataByCustomerIdAPI):
    def __init__(self, order_data_spi: GetOrderDataByCustomerIdSPI) -> None:
        self._order_data_spi = order_data_spi

    def get_order_by_customer_id(self, customer_id: Identifier) -> list[OrderData]:
        result = self._order_data_spi.get_order_data_by_customer_id(
            customer_id=customer_id
        )
        return result
