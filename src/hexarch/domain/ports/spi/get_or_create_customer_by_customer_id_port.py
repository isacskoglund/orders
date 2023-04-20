from typing import Protocol
from dataclasses import dataclass
from models.identifiers import CustomerId
from models.user import Customer


class GetOrCreateCustomerByCustomerIdPort(Protocol):
    # Result

    @dataclass(frozen=True)
    class GetOrCreateCustomerByIdResult:
        pass

    class SuccessfullyGotOrCreatedCustomerByIdResult(GetOrCreateCustomerByIdResult):
        customer: Customer
        customer_was_created: bool

    # Port

    def get_or_create_customer_by_customer_id(
        self, customer_id: CustomerId
    ) -> GetOrCreateCustomerByIdResult:
        raise NotImplementedError
