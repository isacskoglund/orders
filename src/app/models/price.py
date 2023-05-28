from django.db import models
from django.core.exceptions import ValidationError


def validate_currency_code(code: str):
    if not code.isalpha():
        raise ValidationError("Currency code must contain only alphabetic characters.")
    if len(code) != 3:
        raise ValidationError("Currency code must be exactly 3 characters long.")
    if code.upper() != code:
        raise ValidationError("Currency code must be in uppercase.")


class Currency(models.Model):
    code = models.CharField(
        max_length=3,
        primary_key=True,
        validators=[validate_currency_code],
    )
    name = models.CharField(max_length=50)

    class Meta:  # type: ignore
        db_table = "currency"

    def __repr__(self) -> str:
        return f"Currency(name={self.name}, code={self.code})"


class PriceABC(models.Model):
    price_amount = models.IntegerField()
    price_currency = models.ForeignKey(to=Currency, on_delete=models.PROTECT)
    price_unit = models.CharField(max_length=50)

    class Meta:  # type: ignore
        abstract = True
