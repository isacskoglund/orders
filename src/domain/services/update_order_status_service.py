from domain.models.identifier import Identifier
from domain.ports.api.update_order_status_api import (
    UpdateOrderStatusAPI,
    ExpectednessSetting,
)
from domain.ports.spi.order_persistence_spi import UpdateOrderSPI, GetOrderByOrderIdSPI
from domain.ports.spi.status_update_event_dispatcher_spi import (
    StatusUpdateEventDispatcherSPI,
)
from domain.models.order import PersistedOrder
from domain.models.order_status import (
    Status,
    StatusTransition,
    StatusTransitionProtocol,
)
from domain.models.event import StatusToEventMapper
from domain.errors import InvalidOrderIdError, InsufficientExpectednessError
from typing import Callable


def _validate_transition(
    transition: StatusTransitionProtocol, setting: ExpectednessSetting
) -> bool:
    E = ExpectednessSetting

    # If setting is a requirement, check if it is met.
    if setting is E.REQUIRE_NEXT_UP:
        return transition.is_next_up
    if setting is E.REQUIRE_FORSEEN:
        return transition.is_foreseen

    # If transition has a dangerous property, check if has been allowed.
    if transition.is_abnormal:
        return setting is E.ALLOW_ABNORMAL
    if transition.is_unexpected:
        return setting in {E.ALLOW_ABNORMAL, E.ALLOW_UNEXPECTED}

    # If transition has no dangerous properties, and setting is no requirement.
    return True


class UpdateOrderStatusService(UpdateOrderStatusAPI):
    def __init__(
        self,
        update_order_spi: UpdateOrderSPI,
        get_order_by_order_id_spi: GetOrderByOrderIdSPI,
        status_update_event_dispatcher_spi: StatusUpdateEventDispatcherSPI,
        _validate_transition: Callable[
            [StatusTransitionProtocol, ExpectednessSetting], bool
        ] = _validate_transition,
    ) -> None:
        self._save_new_status = update_order_spi.update_order_status
        self._get_order = get_order_by_order_id_spi.get_order_by_order_id
        self._dispatch_event = status_update_event_dispatcher_spi.dispatch_event
        self._validate_transition = _validate_transition

        event_mapper = StatusToEventMapper()
        self._create_event = event_mapper.create_event

    def update_order_status(
        self,
        order_id: Identifier,
        new_status: Status,
        setting: ExpectednessSetting = ExpectednessSetting.REQUIRE_NEXT_UP,
    ) -> PersistedOrder:
        order = self._get_order_or_raise(order_id)
        transition = StatusTransition(from_status=order.status, to_status=new_status)
        transition_is_invalid = not self._validate_transition(
            transition=transition, setting=setting
        )
        if transition_is_invalid:
            raise InsufficientExpectednessError
        updated_order = self._perform_update(order=order, new_status=new_status)
        return updated_order

    def _get_order_or_raise(self, order_id: Identifier) -> PersistedOrder:
        order = self._get_order(order_id=order_id)
        if order is None:
            raise InvalidOrderIdError(order_id=order_id)
        return order

    def _perform_update(
        self, order: PersistedOrder, new_status: Status
    ) -> PersistedOrder:
        self._save_new_status(order_id=order.id, new_status=new_status)
        updated_order = order.update_status(new_status=new_status)
        event = self._create_event(order=updated_order)
        if event is not None:
            self._dispatch_event(event=event)
        return updated_order
