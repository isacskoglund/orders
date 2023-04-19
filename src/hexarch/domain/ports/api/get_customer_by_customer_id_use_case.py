from typing import Protocol
from dataclasses import dataclass
from models.identifiers import CustomerId
from models.user import Customer

# Result


@dataclass(frozen=True)
class GetCustomerByIdResult:
    pass


class CustomerNotFoundResult(GetCustomerByIdResult):
    pass


class SuccessfullyFoundCustomerByIdResult(GetCustomerByIdResult):
    customer: Customer


# Use Case


class GetCustomerByCustomerIdUseCase(Protocol):
    def get_customer_by_customer_id(self, customer: CustomerId) -> Customer:
        raise NotImplementedError
