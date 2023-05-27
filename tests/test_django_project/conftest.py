from .factories import (
    CustomerFactory,
    ShippingAddressFactory,
    ProductFactory,
    ProductVersionFactory,
    OrderFactory,
    LineItemFactory,
    CurrencyFactory,
)
from pytest_factoryboy import register

_factories = (
    CustomerFactory,
    ShippingAddressFactory,
    ProductFactory,
    ProductVersionFactory,
    OrderFactory,
    LineItemFactory,
    CurrencyFactory,
)

for factory in _factories:
    register(factory)
