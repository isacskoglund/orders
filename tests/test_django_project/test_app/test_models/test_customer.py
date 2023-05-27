# type: ignore

from test_django_project.factories import CustomerFactory
from app.models import Customer
from uuid import UUID
import pytest


def test_customer(customer_factory: CustomerFactory):
    customer = customer_factory.build()

    assert isinstance(customer.id, UUID)
