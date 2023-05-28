# type: ignore

from tests.test_django_project.factories import CurrencyFactory
from app.models import Currency

import pytest
from django.core.exceptions import ValidationError


@pytest.mark.parametrize(
    "code",
    ("aaaa", "AAAA", "Aa", "a", "", "aaa", "aAA"),
)
@pytest.mark.django_db
def test_currency_code_invalid(
    code: str,
    currency_factory: CurrencyFactory,
) -> None:
    currency: Currency = currency_factory.build(code=code)

    with pytest.raises(ValidationError):
        currency.full_clean()


@pytest.mark.parametrize("code", ("EEE", "JEK", "EUR"))
@pytest.mark.django_db
def test_currency_code_valid(code: str, currency_factory: CurrencyFactory) -> None:
    currency: Currency = currency_factory.build(code=code)

    try:
        currency.full_clean()
    except ValidationError as e:
        assert False, f"Raised {e}."
