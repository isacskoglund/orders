from domain.models.order_status import StatusTransitionProtocol
from domain.utils.singleton_meta import SingletonMeta
from typing import Protocol
from enum import Enum, auto


class ExpectednessSetting(Enum):
    REQUIRE_NEXT_UP = auto()
    REQUIRE_FORSEEN = auto()
    ALLOW_UNEXPECTED = auto()
    ALLOW_ABNORMAL = auto()


class TransitionValidatorProtocol(Protocol):
    @classmethod
    def validate_transition(
        cls, transition: StatusTransitionProtocol, setting: ExpectednessSetting
    ) -> bool:
        ...


class TransitionValidator(metaclass=SingletonMeta):
    @classmethod
    def validate_transition(
        cls, transition: StatusTransitionProtocol, setting: ExpectednessSetting
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
