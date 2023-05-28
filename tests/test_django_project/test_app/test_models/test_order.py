# type: ignore

from app.models.order import ShippingAddress, Order, LineItem
from app.models.customer import Customer
from tests.test_django_project.factories import (
    ShippingAddressFactory,
    OrderFactory,
    LineItemFactory,
    CustomerFactory,
)

import pytest
from django.core.exceptions import ValidationError


def test_shipping_address(shipping_address_factory: ShippingAddressFactory):
    address: ShippingAddress = ShippingAddressFactory.build()

    assert address.address_line2 is None


@pytest.mark.django_db
def test_order_invalid_args(
    customer_factory: CustomerFactory,
    shipping_address_factory: ShippingAddressFactory,
) -> None:
    # Arrange
    customer = customer_factory.create()
    address = shipping_address_factory.create()

    # Act / Assert
    order = Order(customer=customer, status=Order.StatusChoices.ACCEPTED_BY_INVENTORY)
    with pytest.raises(ValidationError) as e:
        order.full_clean()
    print(e)

    order = Order(
        status=Order.StatusChoices.ACCEPTED_BY_INVENTORY, shipping_address=address
    )
    with pytest.raises(ValidationError):
        order.full_clean()


@pytest.mark.django_db
def test_order_line_items_relation(
    order_factory: OrderFactory,
    line_item_factory: LineItemFactory,
) -> None:
    # Arrange
    order: Order = order_factory.create()
    line_items: set[LineItem] = set()
    for _ in range(4):
        line_items.add(line_item_factory(order=order))

    # Act
    order_line_items_set = set(order.line_items.all())

    # Assert
    assert order_line_items_set == line_items


@pytest.mark.django_db
def test_order_customer_relation(
    order_factory: OrderFactory, customer_factory: CustomerFactory
) -> None:
    # Arrange
    customer: Customer = customer_factory.create()

    # Act
    order_set: set[Order] = set()
    for _ in range(4):
        order_set.add(order_factory(customer=customer))
    customer_orders_set = set(customer.orders.all())

    # Assert
    assert customer_orders_set == order_set
