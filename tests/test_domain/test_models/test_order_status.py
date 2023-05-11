from domain.models.order_status import (
    Status,
    Expectedness,
    StatusTransition,
    TransitionToExpectednessMapper,
)
from dataclasses import dataclass
from pytest import fixture


@dataclass
class ExpectednessMapperDummy:
    current_expectedness: Expectedness = Expectedness.ABNORMAL

    def get_expectedness(self, from_status: Status, to_status: Status) -> Expectedness:
        return self.current_expectedness


@fixture
def expectedness_mapper_dummy() -> ExpectednessMapperDummy:
    return ExpectednessMapperDummy()


def test_is_properties(expectedness_mapper_dummy: ExpectednessMapperDummy) -> None:
    get_transition = lambda: StatusTransition(
        from_status=Status.PENDING,
        to_status=Status.ACCEPTED_BY_INVENTORY,
        _expectedness_mapper=expectedness_mapper_dummy,
    )

    expectedness_mapper_dummy.current_expectedness = Expectedness.ABNORMAL
    transition = get_transition()
    assert transition.is_abnormal is True
    assert transition.is_unexpected is True
    assert transition.is_foreseen is False
    assert transition.is_next_up is False

    expectedness_mapper_dummy.current_expectedness = Expectedness.UNEXPECTED
    transition = get_transition()
    assert transition.is_abnormal is False
    assert transition.is_unexpected is True
    assert transition.is_foreseen is False
    assert transition.is_next_up is False

    expectedness_mapper_dummy.current_expectedness = Expectedness.FORESEEN
    transition = get_transition()
    assert transition.is_abnormal is False
    assert transition.is_unexpected is False
    assert transition.is_foreseen is True
    assert transition.is_next_up is False

    expectedness_mapper_dummy.current_expectedness = Expectedness.NEXT_UP
    transition = get_transition()
    assert transition.is_abnormal is False
    assert transition.is_unexpected is False
    assert transition.is_foreseen is True
    assert transition.is_next_up is True


class TestTransitionToExpectednessMapper:
    def test_get_expectedness(self) -> None:
        for from_status in Status:
            for to_status in Status:
                row = TransitionToExpectednessMapper._status_to_index_map[from_status]
                column = TransitionToExpectednessMapper._status_to_index_map[to_status]
                expectedness_key = (
                    TransitionToExpectednessMapper._transition_to_expectedness_matrix[
                        row
                    ][column]
                )
                expectedness = TransitionToExpectednessMapper._key_to_expectedness_map[
                    expectedness_key
                ]
                assert (
                    TransitionToExpectednessMapper._indices_to_key(
                        from_index=row, to_index=column
                    )
                    == expectedness_key
                )
                assert (
                    TransitionToExpectednessMapper.get_expectedness(
                        from_status=from_status, to_status=to_status
                    )
                    == expectedness
                )

    def test_mapper_is_singleton(self) -> None:
        mapper1 = TransitionToExpectednessMapper()
        mapper2 = TransitionToExpectednessMapper()

        assert mapper1 is mapper2
