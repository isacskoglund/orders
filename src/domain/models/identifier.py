from typing import Protocol


class Identifier(Protocol):
    """
    Abstract identifier class.
    Implementation should make each instance unique to the object it represents.
    """
