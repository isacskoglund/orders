from __future__ import annotations
from identifiers import OrderId, ProductId, ProductVersionId
from identifiers import CustomerId
from enum import Enum
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Address:
    pass


@dataclass(frozen=True)
class RequestedOrder:
    @dataclass(frozen=True)
    class Item:
        product_id: ProductId
        quantity: int

    customer_id: CustomerId
    shipping_address: Address
    items: list[Item]

    def get_product_ids(self) -> list[ProductId]:
        return [item.product_id for item in self.items]

    def to_versioned_order(
        self, product_versions: dict[ProductId, ProductVersionId]
    ) -> VersionedOrder:
        items = [
            VersionedOrder.Item(
                product_id=item.product_id,
                quantity=item.quantity,
                product_version_id=product_versions[ProductId],
            )
            for item in self.items
        ]
        return VersionedOrder(
            customer_id=self.customer_id,
            shipping_address=self.shipping_address,
            items=items,
        )


class VersionedOrder(RequestedOrder):
    class Item(RequestedOrder.Item):
        product_version_id: ProductVersionId

    def to_persisted_order(
        self, id: OrderId, status: PersistedOrder.Status | None = None
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


class PersistedOrder(VersionedOrder):
    class Status(Enum):
        WAITING_FOR_INVENTORY = 1
        ACCEPTED_BY_INVENTORY = 2
        PAID = 3
        NO_LONGER_CANCELABLE = 4
        SHIPPED = 5
        DELIVERED = 6
        CANCELLED = 7

    id: OrderId
    status: Status = Status.WAITING_FOR_INVENTORY

    def update_status(self, new_status: Status) -> PersistedOrder:
        return replace(self, status=new_status)
