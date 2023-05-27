# type: ignore

import factory
from factory.django import DjangoModelFactory
from app.models import (
    Customer,
    Order,
    ShippingAddress,
    LineItem,
    Product,
    ProductVersion,
    Currency,
)


class ShippingAddressFactory(DjangoModelFactory):
    class Meta:
        model = ShippingAddress

    address_line1 = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state")
    postal_code = factory.Faker("postcode")
    country = factory.Faker("country")

    class Params:
        with_address_line2 = factory.Trait(
            address_line2=factory.Faker("secondary_address")
        )


class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = Customer


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    class Params:
        with_current_product_version = factory.Trait(
            current_product_version=factory.RelatedFactory(".ProductVersionFactory")
        )


class ProductVersionFactory(DjangoModelFactory):
    class Meta:
        model = ProductVersion

    product = factory.SubFactory(ProductFactory)


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    customer = factory.SubFactory(CustomerFactory)
    status = factory.Iterator(Order.StatusChoices.values)
    shipping_address = factory.SubFactory(ShippingAddressFactory)


class LineItemFactory(DjangoModelFactory):
    class Meta:
        model = LineItem

    order = factory.SubFactory(OrderFactory)
    product_version = factory.SubFactory(ProductVersionFactory)


class CurrencyFactory(DjangoModelFactory):
    class Meta:
        model = Currency

    code = factory.Faker("currency_code")
    name = factory.Faker("currency_name")
