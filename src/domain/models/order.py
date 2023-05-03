from __future__ import annotations
from .identifier import Identifier
from enum import Enum
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Address:
    pass


@dataclass(frozen=True)
class RequestedOrder:
    @dataclass(frozen=True)
    class Item:
        product_id: Identifier
        quantity: int

    customer_id: Identifier
    shipping_address: Address
    items: list[Item]

    def get_product_ids(self) -> list[Identifier]:
        return [item.product_id for item in self.items]

    def to_versioned_order(
        self, product_versions: dict[Identifier, Identifier]
    ) -> VersionedOrder:
        items = [
            VersionedOrder.Item(
                product_id=item.product_id,
                quantity=item.quantity,
                product_version_id=product_versions[item.product_id],
            )
            for item in self.items
        ]
        return VersionedOrder(
            customer_id=self.customer_id,
            shipping_address=self.shipping_address,
            items=items,
        )


@dataclass(frozen=True)
class VersionedOrder(RequestedOrder):
    items: list[Item]

    @dataclass(frozen=True)
    class Item(RequestedOrder.Item):
        product_version_id: Identifier

    def to_persisted_order(
        self, id: Identifier, status: PersistedOrder.Status | None = None
    ):
        args = {
            "customer_id": self.customer_id,
            "shipping_address": self.shipping_address,
            "items": self.items,
            "id": id,
        }
        if status is not None:
            args["status"] = status

        return PersistedOrder(**args)


@dataclass(frozen=True)
class PersistedOrder(VersionedOrder):
    class Status(Enum):
        REQUESTED = 1
        VALIDATED = 2
        PAID = 3
        NO_LONGER_CANCELABLE = 4
        SHIPPED = 5
        DELIVERED = 6
        CANCELLED = 7

    id: Identifier
    status: Status = Status.REQUESTED

    def update_status(self, new_status: Status) -> PersistedOrder:
        return replace(self, status=new_status)
