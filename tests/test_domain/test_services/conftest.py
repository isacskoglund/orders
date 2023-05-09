from __future__ import annotations
from domain.ports.spi.order_persistence_spi import (
    GetOrderByOrderIdSPI,
    UpdateOrderSPI,
    SaveOrderSPI,
)
from domain.ports.spi.product_catalogue_spi import GetProductVersionIdsSPI
from domain.ports.spi.status_update_event_dispatcher_spi import (
    StatusUpdateEventDispatcherSPI,
)
from domain.models.identifier import Identifier
from domain.models.order_status import Status
from domain.models.order import PersistedOrder, VersionedOrder
from domain.models.event import DispatchableEvent, StatusToEventMapperProtocol
from typing import Callable
from pytest import fixture
from dataclasses import dataclass, field


class UpdateOrderDummy(UpdateOrderSPI):
    statuses: dict[Identifier, Status] = {}

    def update_order_status(self, order_id: Identifier, new_status: Status) -> None:
        self.statuses[order_id] = new_status

    def reset(self) -> None:
        self.statuses = {}

    def read(self) -> dict[Identifier, Status]:
        return self.statuses

    def is_empty(self) -> bool:
        return self.statuses == {}


@dataclass
class SaveOrderDummy(SaveOrderSPI):
    id_generator: Callable[[], Identifier]

    orders: dict[Identifier, PersistedOrder] = field(default_factory=dict)

    def save_order(self, versioned_order: VersionedOrder) -> PersistedOrder:
        persisted_order = versioned_order.to_persisted_order(id=id)
        self.orders[id] = persisted_order
        return persisted_order

    def reset(self) -> None:
        self.orders = {}

    def read(self) -> dict[Identifier, PersistedOrder]:
        return self.orders

    def is_empty(self) -> bool:
        return self.orders == {}


@dataclass
class GetProductVersionIdsDummy(GetProductVersionIdsSPI):
    product_version_ids: dict[Identifier, Identifier] = field(default_factory=dict)
    invalid_ids: set[Identifier] = field(default_factory=set)
    ids_without_product_version_id: set[Identifier] = field(default_factory=set)

    def get_product_versions(
        self, product_ids: list[Identifier]
    ) -> GetProductVersionIdsSPI.Result:
        return GetProductVersionIdsSPI.Result(
            product_version_ids=self.product_version_ids,
            invalid_ids=self.invalid_ids,
            ids_without_product_version_id=self.ids_without_product_version_id,
        )


class GetOrderByOrderIdDummy(GetOrderByOrderIdSPI):
    orders: dict[Identifier, PersistedOrder] = {}

    def get_order_by_order_id(self, order_id: Identifier) -> PersistedOrder | None:
        return self.orders.get(order_id)

    def reset(self) -> None:
        self.orders = {}

    def add(self, order: PersistedOrder) -> None:
        self.orders[order.id] = order


class EventDispatcherDummy(StatusUpdateEventDispatcherSPI):
    dispatched_events: list[DispatchableEvent] = []

    def dispatch_event(self, event: DispatchableEvent) -> None:
        self.dispatched_events.append(event)

    def reset(self) -> None:
        self.dispatched_events = []

    def read(self) -> list[DispatchableEvent]:
        return self.dispatched_events

    def is_empty(self) -> bool:
        return self.dispatched_events == []


@dataclass
class StatusToEventMapperDummy(StatusToEventMapperProtocol):
    event_type: type[DispatchableEvent] | None = None

    def map_status_to_event(self, status: Status) -> type[DispatchableEvent] | None:
        return self.event_type


@dataclass
class EventTest(DispatchableEvent):
    ...


@fixture
def update_order_dummy() -> UpdateOrderDummy:
    return UpdateOrderDummy


@fixture
def save_order_dummy(id_generator) -> SaveOrderDummy:
    return SaveOrderDummy(id_generator=id_generator)


@fixture
def get_product_version_ids_dummy() -> GetProductVersionIdsDummy:
    return GetProductVersionIdsDummy()


@fixture
def get_order_by_id_dummy() -> GetOrderByOrderIdDummy:
    return GetOrderByOrderIdDummy()


@fixture
def event_dispatcher_dummy() -> EventDispatcherDummy:
    return EventDispatcherDummy()


@fixture
def status_to_event_mapper_dummy() -> StatusToEventMapperDummy:
    return StatusToEventMapperDummy()
