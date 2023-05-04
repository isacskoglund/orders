from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Callable
from enum import Enum


class Singleton(type):
    """
    Metaclass for creating singleton classes.
    """

    _instances = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Status(Enum):
    PENDING = "Order has been validated and is ready to be reviewed by inventory."
    ACCEPTED_BY_INVENTORY = (
        "Order has been accepted by inventory and is ready to be paid."
    )
    PAID = "Order has been paid and is ready to be shipped."
    SHIPPED = "Order has been shipped."
    DELIVERED = "Order has been delivered."
    CANCELLED = "Order has been cancelled."


@dataclass(frozen=True)
class StatusTransition:
    class Expectedness(Enum):
        ABNORMAL = 0
        UNEXPECTED = 1
        FORESEEN = 2
        NEXT_UP = 3

    from_status: Status
    to_status: Status
    _custom_expectedness_mapper: Optional[
        Callable[[Status, Status], StatusTransition.Expectedness]
    ] = None

    def _get_expectedness(
        self, from_status: Status, to_status: Status
    ) -> StatusTransition.Expectedness:
        expectedness_mapper = self._custom_expectedness_mapper
        if expectedness_mapper is None:
            expectedness_mapper = TransitionToExpectednessMapper.get_expectedness
        return expectedness_mapper(from_status=from_status, to_status=to_status)

    @property
    def expectedness(self) -> StatusTransition.Expectedness:
        return self._get_expectedness(
            from_status=self.from_status, to_status=self.to_status
        )

    @property
    def is_abnormal(self) -> bool:
        return self.expectedness.value <= StatusTransition.Expectedness.ABNORMAL.value

    @property
    def is_unexpected(self) -> bool:
        return self.expectedness.value <= StatusTransition.Expectedness.UNEXPECTED.value

    @property
    def is_foreseen(self) -> bool:
        return self.expectedness.value >= StatusTransition.Expectedness.FORESEEN.value

    @property
    def is_next_up(self) -> bool:
        return self.expectedness.value >= StatusTransition.Expectedness.NEXT_UP.value


class TransitionToExpectednessMapper(metaclass=Singleton):
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
        0: StatusTransition.Expectedness.ABNORMAL,
        1: StatusTransition.Expectedness.UNEXPECTED,
        2: StatusTransition.Expectedness.FORESEEN,
        3: StatusTransition.Expectedness.NEXT_UP,
    }

    @classmethod
    def _indices_to_key(cls, from_index: int, to_index: int) -> int:
        return cls._transition_to_expectedness_matrix[from_index][to_index]

    @classmethod
    def get_expectedness(
        cls, from_status: Status, to_status: Status
    ) -> StatusTransition.Expectedness:
        from_index = cls._status_to_index_map[from_status]
        to_index = cls._status_to_index_map[to_status]
        expectedness_key = cls._indices_to_key(from_index=from_index, to_index=to_index)
        expectedness = cls._key_to_expectedness_map[expectedness_key]
        return expectedness
