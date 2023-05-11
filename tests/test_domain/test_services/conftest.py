from __future__ import annotations
from domain.ports.spi.product_catalogue_spi import GetProductVersionIdsSPI
from domain.models.identifier import Identifier
from domain.models.order_status import Status
from domain.models.order import OrderData, PersistedOrder, VersionedOrder
from domain.models.event import DispatchableEvent
from pytest import fixture
from dataclasses import dataclass, field


@dataclass
class UpdateOrderDummy:
    statuses: dict[Identifier, Status] = field(default_factory=dict)

    def update_order_status(self, order_id: Identifier, new_status: Status) -> None:
        self.statuses[order_id] = new_status

    def read(self) -> dict[Identifier, Status]:
        return self.statuses

    def is_empty(self) -> bool:
        return self.statuses == {}


@dataclass
class SaveOrderDummy:
    persisted_order_to_return: PersistedOrder

    versioned_orders_saved: list[VersionedOrder] = field(default_factory=list)

    def save_order(self, versioned_order: VersionedOrder) -> PersistedOrder:
        self.versioned_orders_saved.append(versioned_order)
        return self.persisted_order_to_return

    def read(self) -> list[VersionedOrder]:
        return self.versioned_orders_saved

    def is_empty(self) -> bool:
        return self.versioned_orders_saved == []


@dataclass
class GetProductVersionIdsDummy:
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


@dataclass
class GetOrderByOrderIdDummy:
    orders: dict[Identifier, PersistedOrder] = field(default_factory=dict)

    def get_order_by_order_id(self, order_id: Identifier) -> PersistedOrder | None:
        return self.orders.get(order_id)

    def reset(self) -> None:
        self.orders = {}

    def add(self, order: PersistedOrder) -> None:
        self.orders[order.id] = order


@dataclass
class EventDispatcherDummy:
    dispatched_events: list[DispatchableEvent] = field(default_factory=list)

    def dispatch_event(self, event: DispatchableEvent) -> None:
        self.dispatched_events.append(event)

    def read(self) -> list[DispatchableEvent]:
        return self.dispatched_events

    def is_empty(self) -> bool:
        return self.dispatched_events == []


@dataclass
class StatusToEventMapperDummy:
    event_type: DispatchableEvent.EventType | None = None

    def map_status_to_event_type(
        self, status: Status
    ) -> DispatchableEvent.EventType | None:
        return self.event_type


@dataclass
class OrderDataByOrderIdDummy:
    order_data: OrderData | None = None

    def get_order_data_by_order_id(self, order_id: Identifier) -> OrderData | None:
        return self.order_data


@dataclass
class OrderDataByCustomerIdDummy:
    order_data: list[OrderData] = field(default_factory=list)

    def get_order_data_by_customer_id(self, customer_id: Identifier) -> list[OrderData]:
        return self.order_data


@fixture
def update_order_dummy() -> UpdateOrderDummy:
    return UpdateOrderDummy()


@fixture
def save_order_dummy(persisted_order: PersistedOrder) -> SaveOrderDummy:
    return SaveOrderDummy(persisted_order_to_return=persisted_order)


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


@fixture
def order_data_by_order_id_dummy() -> OrderDataByOrderIdDummy:
    return OrderDataByOrderIdDummy()


@fixture
def order_data_by_customer_id_dummy() -> OrderDataByCustomerIdDummy:
    return OrderDataByCustomerIdDummy()
