from enum import Enum
from dataclasses import dataclass
from .identifier import Identifier


@dataclass(frozen=True)
class User:
    id: Identifier


@dataclass(frozen=True)
class Customer(User):
    id: Identifier
