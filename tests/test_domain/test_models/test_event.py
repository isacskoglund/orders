from domain.models.order_status import Status
from domain.models.event import StatusToEventMapper


def test_map_status_to_event() -> None:
    mapper = StatusToEventMapper
    for status in Status:
        expected_event_type = None
        if status in StatusToEventMapper.status_to_event_type_map:
            expected_event_type = StatusToEventMapper.status_to_event_type_map[status]
        assert expected_event_type == mapper.map_status_to_event_type(status=status)


def test_mapper_is_singleton() -> None:
    mapper1 = StatusToEventMapper()
    mapper2 = StatusToEventMapper()
    assert isinstance(mapper1, StatusToEventMapper)
    assert mapper1 is mapper2
