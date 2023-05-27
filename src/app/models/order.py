from django.db import models
from uuid import uuid4
from .customer import Customer
from .product import ProductVersion


class ShippingAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    class Meta:  # type: ignore
        db_table = "shipping_address"


class Order(models.Model):
    class StatusChoices(models.IntegerChoices):
        CANCELLED = 0
        PENDING = 1
        ACCEPTED_BY_INVENTORY = 2
        PAID = 3
        SHIPPED = 4
        DELIVERED = 5

    id = models.UUIDField(primary_key=True, default=uuid4)
    customer = models.ForeignKey(
        to=Customer, related_name="orders", on_delete=models.PROTECT
    )
    status = models.IntegerField(
        choices=StatusChoices.choices,
    )
    shipping_address = models.OneToOneField(
        ShippingAddress, on_delete=models.PROTECT, related_name="order"
    )

    class Meta:  # type: ignore
        db_table = "order"


class LineItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    order = models.ForeignKey(
        to=Order, on_delete=models.PROTECT, related_name="line_items"
    )
    product_version = models.ForeignKey(to=ProductVersion, on_delete=models.PROTECT)

    class Meta:  # type: ignore
        db_table = "line_item"
