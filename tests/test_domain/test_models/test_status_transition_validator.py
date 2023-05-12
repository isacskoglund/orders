from domain.models.order_status import Status
from domain.models.status_transition_validator import (
    ExpectednessSetting,
    TransitionValidator,
)
from test_domain.dummies import TransitionDummy
import pytest


@pytest.fixture
def transition_dummy() -> TransitionDummy:
    return TransitionDummy(from_status=Status.PENDING, to_status=Status.PENDING)


def test_transition_validator(transition_dummy: TransitionDummy) -> None:
    E = ExpectednessSetting

    def is_valid(setting: E):
        return TransitionValidator.validate_transition(
            transition=transition_dummy, setting=setting
        )

    # validate with all 4 available settings for each state of the dummy.

    transition_dummy.set_abnormal()
    assert is_valid(E.ALLOW_ABNORMAL) is True
    assert is_valid(E.ALLOW_UNEXPECTED) is False
    assert is_valid(E.REQUIRE_FORSEEN) is False
    assert is_valid(E.REQUIRE_NEXT_UP) is False

    transition_dummy.set_unexpected()
    assert is_valid(E.ALLOW_ABNORMAL) is True
    assert is_valid(E.ALLOW_UNEXPECTED) is True
    assert is_valid(E.REQUIRE_FORSEEN) is False
    assert is_valid(E.REQUIRE_NEXT_UP) is False

    transition_dummy.set_foreseen()
    assert is_valid(E.ALLOW_ABNORMAL) is True
    assert is_valid(E.ALLOW_UNEXPECTED) is True
    assert is_valid(E.REQUIRE_FORSEEN) is True
    assert is_valid(E.REQUIRE_NEXT_UP) is False

    transition_dummy.set_next_up()
    assert is_valid(E.ALLOW_ABNORMAL) is True
    assert is_valid(E.ALLOW_UNEXPECTED) is True
    assert is_valid(E.REQUIRE_FORSEEN) is True
    assert is_valid(E.REQUIRE_NEXT_UP) is True


def test_transition_validator_is_singleton() -> None:
    validator1 = TransitionValidator()
    validator2 = TransitionValidator()
    assert validator1 is validator2
