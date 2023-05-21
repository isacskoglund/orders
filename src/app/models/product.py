from django.db import models
from uuid import uuid4
from .price import PriceABC


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    current_product_version = models.OneToOneField(
        to="ProductVersion", null=True, on_delete=models.PROTECT, related_name="+"
    )

    class Meta:  # type: ignore
        db_table = "product"


class ProductVersion(PriceABC):
    id = models.UUIDField(primary_key=True, default=uuid4)
    product = models.ForeignKey(to=Product, on_delete=models.PROTECT)

    class Meta(PriceABC.Meta):
        db_table = "product_version"
