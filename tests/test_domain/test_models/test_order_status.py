from domain.models.order_status import (
    Status,
    StatusTransition,
    TransitionToExpectednessMapper,
)
from pytest import fixture
from dataclasses import dataclass


@dataclass
class ExpectednessMapperDummy:
    current_expectedness: StatusTransition.Expectedness

    def get_expectedness(
        self, from_status: Status, to_status: Status
    ) -> StatusTransition.Expectedness:
        return self.current_expectedness


class TestStatusTransition:
    def test_is_properties(self) -> None:
        E = StatusTransition.Expectedness
        mapper_dummy = ExpectednessMapperDummy(current_expectedness=E.ABNORMAL)
        transition = StatusTransition(
            from_status=Status.PENDING,
            to_status=Status.ACCEPTED_BY_INVENTORY,
            _custom_expectedness_mapper=mapper_dummy.get_expectedness,
        )

        mapper_dummy.current_expectedness = E.ABNORMAL
        assert transition.is_abnormal is True
        assert transition.is_unexpected is True
        assert transition.is_foreseen is False
        assert transition.is_next_up is False

        mapper_dummy.current_expectedness = E.UNEXPECTED
        assert transition.is_abnormal is False
        assert transition.is_unexpected is True
        assert transition.is_foreseen is False
        assert transition.is_next_up is False

        mapper_dummy.current_expectedness = E.FORESEEN
        assert transition.is_abnormal is False
        assert transition.is_unexpected is False
        assert transition.is_foreseen is True
        assert transition.is_next_up is False

        mapper_dummy.current_expectedness = E.NEXT_UP
        assert transition.is_abnormal is False
        assert transition.is_unexpected is False
        assert transition.is_foreseen is True
        assert transition.is_next_up is True

    def test_expectedness(self) -> None:
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
