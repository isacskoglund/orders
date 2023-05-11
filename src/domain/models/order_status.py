from __future__ import annotations
from domain.utils.singleton_meta import SingletonMeta
from dataclasses import dataclass
from typing import Protocol
from enum import Enum, auto


class Status(Enum):
    PENDING = auto()
    ACCEPTED_BY_INVENTORY = auto()
    PAID = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()


class Expectedness(Enum):
    ABNORMAL = auto()
    UNEXPECTED = auto()
    FORESEEN = auto()
    NEXT_UP = auto()


class StatusTransitionProtocol(Protocol):
    from_status: Status
    to_status: Status
    is_abnormal: bool
    is_unexpected: bool
    is_foreseen: bool
    is_next_up: bool


class TransitionToExpectednessProtocol(Protocol):
    @classmethod
    def get_expectedness(cls, from_status: Status, to_status: Status) -> Expectedness:
        ...


class TransitionToExpectednessMapper(metaclass=SingletonMeta):
    """
    Singleton that maps an order status transition
    to a member of `Expectedness`.
    Status transitions are tuples `(from_status, to_status)`.
    """

    _status_to_index_map = {
        # Assigns each member of Status to a unique index.
        Status.PENDING: 0,
        Status.ACCEPTED_BY_INVENTORY: 1,
        Status.PAID: 2,
        Status.SHIPPED: 3,
        Status.DELIVERED: 4,
        Status.CANCELLED: 5,
    }

    _transition_to_expectedness_matrix = (
        # Assigns each tuple `(from_status, to_status)` to a member of `Expectedness`.
        # Row indices are given by `from_status`.
        # Column indices are given by `to_status`.
        # Values at each position are keys and relate to a specific member of `Expectedness`.
        #
        # P, A, P, S, D, C
        (0, 3, 2, 2, 2, 1),  # PENDING
        (1, 0, 3, 2, 2, 1),  # ACCEPTED_BY_INVENTORY
        (0, 0, 0, 3, 2, 1),  # PAID
        (0, 0, 0, 0, 3, 1),  # SHIPPED
        (0, 0, 0, 0, 0, 0),  # DELIVERED
        (0, 0, 0, 0, 0, 0),  # CANCELLED
    )

    _key_to_expectedness_map = {
        # Assigns each key to a member of `Expectedness`.
        0: Expectedness.ABNORMAL,
        1: Expectedness.UNEXPECTED,
        2: Expectedness.FORESEEN,
        3: Expectedness.NEXT_UP,
    }

    @classmethod
    def _indices_to_key(cls, from_index: int, to_index: int) -> int:
        return cls._transition_to_expectedness_matrix[from_index][to_index]

    @classmethod
    def get_expectedness(cls, from_status: Status, to_status: Status) -> Expectedness:
        from_index = cls._status_to_index_map[from_status]
        to_index = cls._status_to_index_map[to_status]
        expectedness_key = cls._indices_to_key(from_index=from_index, to_index=to_index)
        expectedness = cls._key_to_expectedness_map[expectedness_key]
        return expectedness


@dataclass(frozen=True)
class StatusTransition:
    from_status: Status
    to_status: Status
    _expectedness_mapper: TransitionToExpectednessProtocol = (
        TransitionToExpectednessMapper
    )

    @property
    def _expectedness(self) -> Expectedness:
        return self._expectedness_mapper.get_expectedness(
            from_status=self.from_status, to_status=self.to_status
        )

    @property
    def is_abnormal(self) -> bool:
        return self._expectedness in {Expectedness.ABNORMAL}

    @property
    def is_unexpected(self) -> bool:
        return self._expectedness in {Expectedness.ABNORMAL, Expectedness.UNEXPECTED}

    @property
    def is_foreseen(self) -> bool:
        return self._expectedness in {Expectedness.FORESEEN, Expectedness.NEXT_UP}

    @property
    def is_next_up(self) -> bool:
        return self._expectedness in {Expectedness.NEXT_UP}
