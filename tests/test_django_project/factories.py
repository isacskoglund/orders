import factory  # type: ignore
from app.models.customer import Customer


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:  # type: ignore
        model = Customer
