from domain.models.order import PersistedOrder
from domain.models.order_status import Status
from domain.models.event import StatusToEventMapper


def test_map_status_to_event() -> None:
    mapper = StatusToEventMapper
    for status in Status:
        expected_result = None
        if status in StatusToEventMapper.status_to_event_map:
            expected_result = StatusToEventMapper.status_to_event_map[status]
        assert expected_result == mapper.map_status_to_event(status=status)


def test_mapper_is_singleton() -> None:
    mapper1 = StatusToEventMapper()
    mapper2 = StatusToEventMapper()
    assert isinstance(mapper1, StatusToEventMapper)
    assert mapper1 is mapper2
