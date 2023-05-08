from typing import Callable
from domain.models.order import PersistedOrder
from domain.models.order_status import Status
from domain.models.event import StatusToEventMapper


def test_map_status_to_event() -> None:
    mapper = StatusToEventMapper()
    for status in Status:
        expected_result = None
        if status in mapper.status_to_event_map:
            expected_result = mapper.status_to_event_map[status]
        assert expected_result == mapper.map_status_to_event(status=status)


def test_create_event(persisted_order: PersistedOrder) -> None:
    mapper = StatusToEventMapper()
    for status in Status:
        updated_order = persisted_order.update_status(new_status=status)
        event = mapper.create_event(order=updated_order)
        if status in mapper.status_to_event_map:
            assert isinstance(event, mapper.status_to_event_map[status])
        else:
            assert event is None
