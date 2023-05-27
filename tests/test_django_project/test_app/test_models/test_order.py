# type: ignore

from app.models.order import ShippingAddress, Order, LineItem
from tests.test_django_project.factories import (
    ShippingAddressFactory,
    OrderFactory,
    LineItemFactory,
)


def test_shipping_address(shipping_address_factory: ShippingAddressFactory):
    address: ShippingAddress = ShippingAddressFactory.build()

    assert address.address_line2 is None


def test_order(order_factory: OrderFactory):
    order: Order = order_factory.build()

    assert isinstance(order.shipping_address, ShippingAddress)
    assert isinstance(order.shipping_address, ShippingAddress)
