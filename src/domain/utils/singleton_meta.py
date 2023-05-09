from typing import Any


class SingletonMeta(type):

    """
    Metaclass for creating singleton classes.
    """

    _instances = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]