from __future__ import annotations
from typing import Any, TypeVar, Generic

_T = TypeVar("_T")


class SingletonMeta(type, Generic[_T]):

    """
    Metaclass for creating singleton classes.
    """

    _instances: dict[SingletonMeta[_T], _T] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
