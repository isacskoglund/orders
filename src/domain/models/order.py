from __future__ import annotations
from .identifier import Identifier
from .order_status import Status
from dataclasses import dataclass, replace
from functools import partial


@dataclass(frozen=True)
class Address:
    pass


@dataclass(frozen=True)
class Item:
    product_id: Identifier
    quantity: int


@dataclass(frozen=True)
class VersionedItem(Item):
    product_version_id: Identifier


@dataclass(frozen=True)
class Order:
    customer_id: Identifier
    shipping_address: Address


@dataclass(frozen=True)
class RequestedOrder(Order):
    items: list[Item]

    def get_product_ids(self) -> list[Identifier]:
        return [item.product_id for item in self.items]

    def to_versioned_order(
        self, product_versions: dict[Identifier, Identifier]
    ) -> VersionedOrder:
        items = [
            VersionedItem(
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
class VersionedOrder(Order):
    items: list[VersionedItem]

    def get_product_ids(self) -> list[Identifier]:
        return [item.product_id for item in self.items]

    def to_persisted_order(self, id: Identifier, status: Status | None = None):
        create_persisted_order = partial(
            PersistedOrder,
            customer_id=self.customer_id,
            shipping_address=self.shipping_address,
            items=self.items,
            id=id,
        )
        if status is None:
            return create_persisted_order()
        return create_persisted_order(status=status)


@dataclass(frozen=True)
class PersistedOrder(Order):
    id: Identifier
    items: list[VersionedItem]
    status: Status = Status.PENDING

    def update_status(self, new_status: Status) -> PersistedOrder:
        return replace(self, status=new_status)
