from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator


class Currency(models.Model):
    code = models.CharField(
        max_length=3,
        primary_key=True,
        validators=[MinLengthValidator(3), MaxLengthValidator(3)],
    )
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "currency"


class PriceABC(models.Model):
    price_amount = models.IntegerField()
    price_currency = models.ForeignKey(to=Currency, on_delete=models.PROTECT)
    price_unit = models.CharField(max_length=50)

    class Meta:
        abstract = True
