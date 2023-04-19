from typing import Protocol
from dataclasses import dataclass
from models.identifiers import CustomerId, ProductId
from models.order import Order

# Commands


@dataclass(frozen=True)
class PlaceOrderCommand:
    @dataclass(frozen=True)
    class CommandItem:
        product_id: ProductId
        quantity: int

    customer_id: CustomerId
    items: list[CommandItem]


# Results


@dataclass(frozen=True)
class PlaceOrderResult:
    pass


class InvalidProductResult(PlaceOrderResult):
    product_id: ProductId


class SuccessfullyPlacedOrderResult(PlaceOrderResult):
    new_user_was_created: bool
    order: Order


# Use Case


class PlaceOrderUseCase(Protocol):
    def place_order(self, command: PlaceOrderCommand) -> PlaceOrderResult:
        raise NotImplementedError
