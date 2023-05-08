from domain.models.order_status import (
    Status,
    Expectedness,
    StatusTransition,
    TransitionToExpectednessMapper,
)
from pytest import fixture
from dataclasses import dataclass


@dataclass
class ExpectednessMapperDummy:
    current_expectedness: Expectedness

    def get_expectedness(self, from_status: Status, to_status: Status) -> Expectedness:
        return self.current_expectedness


class TestStatusTransition:
    mapper_dummy = ExpectednessMapperDummy(current_expectedness=Expectedness.ABNORMAL)
    transition = StatusTransition(
        from_status=Status.PENDING,
        to_status=Status.ACCEPTED_BY_INVENTORY,
        _get_expectedness=mapper_dummy.get_expectedness,
    )

    def test_expectedness(self) -> None:
        for expectedness in Expectedness:
            self.mapper_dummy.current_expectedness = expectedness
            assert self.transition._expectedness == expectedness

    def test_is_properties(self) -> None:
        self.mapper_dummy.current_expectedness = Expectedness.ABNORMAL
        assert self.transition.is_abnormal is True
        assert self.transition.is_unexpected is True
        assert self.transition.is_foreseen is False
        assert self.transition.is_next_up is False

        self.mapper_dummy.current_expectedness = Expectedness.UNEXPECTED
        assert self.transition.is_abnormal is False
        assert self.transition.is_unexpected is True
        assert self.transition.is_foreseen is False
        assert self.transition.is_next_up is False

        self.mapper_dummy.current_expectedness = Expectedness.FORESEEN
        assert self.transition.is_abnormal is False
        assert self.transition.is_unexpected is False
        assert self.transition.is_foreseen is True
        assert self.transition.is_next_up is False

        self.mapper_dummy.current_expectedness = Expectedness.NEXT_UP
        assert self.transition.is_abnormal is False
        assert self.transition.is_unexpected is False
        assert self.transition.is_foreseen is True
        assert self.transition.is_next_up is True

    def test_has_correct_default_mapper(self) -> None:
        transition = StatusTransition(
            from_status=Status.PENDING, to_status=Status.ACCEPTED_BY_INVENTORY
        )
        assert (
            transition._get_expectedness
            == TransitionToExpectednessMapper.get_expectedness
        )


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
