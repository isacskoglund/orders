from domain.services.order_data_service import (
    OrderDataByOrderIdService,
    OrderDataByCustomerIdService,
)
from domain.models.order import OrderData
from domain.errors import InvalidOrderIdError
from conftest import OrderDataByOrderIdDummy, OrderDataByCustomerIdDummy
import pytest


def test_by_order_id_service_invalid_order_id(
    order_data_by_order_id_dummy: OrderDataByOrderIdDummy, order_data: OrderData
) -> None:
    service = OrderDataByOrderIdService(order_data_spi=order_data_by_order_id_dummy)

    with pytest.raises(InvalidOrderIdError) as error_info:
        service.get_order_by_order_id(order_id=order_data.id)

    assert error_info.value.order_id == order_data.id


def test_by_order_id_service_success(
    order_data_by_order_id_dummy: OrderDataByOrderIdDummy, order_data: OrderData
) -> None:
    service = OrderDataByOrderIdService(order_data_spi=order_data_by_order_id_dummy)
    order_data_by_order_id_dummy.order_data = order_data

    result = service.get_order_by_order_id(order_id=order_data.id)

    assert result == order_data


def test_by_customer_id_service_empty(
    order_data_by_customer_id_dummy: OrderDataByCustomerIdDummy, order_data: OrderData
) -> None:
    service = OrderDataByCustomerIdService(
        order_data_spi=order_data_by_customer_id_dummy
    )

    result = service.get_order_by_customer_id(customer_id=order_data.customer_id)

    assert result == []


def test_by_customer_id_service_success(
    order_data_by_customer_id_dummy: OrderDataByCustomerIdDummy, order_data: OrderData
) -> None:
    service = OrderDataByCustomerIdService(
        order_data_spi=order_data_by_customer_id_dummy
    )
    expected_result = [order_data] * 5
    order_data_by_customer_id_dummy.order_data_list = expected_result

    result = service.get_order_by_customer_id(customer_id=order_data.customer_id)

    assert result == expected_result
