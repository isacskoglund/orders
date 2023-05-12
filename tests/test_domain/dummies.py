from __future__ import annotations
from domain.ports.spi.product_catalogue_spi import GetProductVersionIdsSPI
from domain.ports.api.update_order_status_api import ExpectednessSetting
from domain.models.identifier import Identifier
from domain.models.order_status import Status, StatusTransitionProtocol
from domain.models.order import OrderData, PersistedOrder, VersionedOrder
from domain.models.event import DispatchableEvent
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

    Result = GetProductVersionIdsSPI.Result

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
    order_data_list: list[OrderData] = field(default_factory=list)

    def get_order_data_by_customer_id(self, customer_id: Identifier) -> list[OrderData]:
        return self.order_data_list


@dataclass
class TransitionDummy:
    from_status: Status
    to_status: Status
    is_abnormal: bool = False
    is_unexpected: bool = False
    is_foreseen: bool = False
    is_next_up: bool = False

    def set_abnormal(self) -> None:
        self.is_abnormal = True
        self.is_unexpected = True
        self.is_foreseen = False
        self.is_next_up = False

    def set_unexpected(self) -> None:
        self.is_abnormal = False
        self.is_unexpected = True
        self.is_foreseen = False
        self.is_next_up = False

    def set_foreseen(self) -> None:
        self.is_abnormal = False
        self.is_unexpected = False
        self.is_foreseen = True
        self.is_next_up = False

    def set_next_up(self) -> None:
        self.is_abnormal = False
        self.is_unexpected = False
        self.is_foreseen = True
        self.is_next_up = True


class TransitionValidatorDummy:
    is_valid: bool = False

    @classmethod
    def validate_transition(
        cls, transition: StatusTransitionProtocol, setting: ExpectednessSetting
    ) -> bool:
        return cls.is_valid

    @classmethod
    def set_valid(cls) -> None:
        cls.is_valid = True

    @classmethod
    def set_invalid(cls) -> None:
        cls.is_valid = False
