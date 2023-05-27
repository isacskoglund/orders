from django.db import models
from uuid import uuid4


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)

    class Meta:  # type: ignore
        db_table = "customer"
