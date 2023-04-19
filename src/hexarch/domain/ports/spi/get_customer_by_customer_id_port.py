from typing import Protocol
from dataclasses import dataclass
from models.identifiers import CustomerId
from models.user import Customer


class GetCustomerByCustomerIdPort(Protocol):
    # Result

    @dataclass(frozen=True)
    class GetCustomerByIdResult:
        pass

    class CustomerNotFoundResult(GetCustomerByIdResult):
        pass

    class SuccessfullyFoundCustomerByIdResult(GetCustomerByIdResult):
        customer: Customer

    # Port

    def get_customer_by_customer_id(
        self, customer: CustomerId
    ) -> GetCustomerByIdResult:
        raise NotImplementedError
