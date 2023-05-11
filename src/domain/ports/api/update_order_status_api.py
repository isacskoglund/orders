from abc import ABC, abstractmethod
from domain.models.identifier import Identifier
from domain.models.order import PersistedOrder
from domain.models.order_status import Status
from enum import Enum, auto


class ExpectednessSetting(Enum):
    REQUIRE_NEXT_UP = auto()
    REQUIRE_FORSEEN = auto()
    ALLOW_UNEXPECTED = auto()
    ALLOW_ABNORMAL = auto()


class UpdateOrderStatusAPI(ABC):
    @abstractmethod
    def update_order_status(
        self,
        order_id: Identifier,
        new_status: Status,
        setting: ExpectednessSetting = ExpectednessSetting.REQUIRE_NEXT_UP,
    ) -> PersistedOrder:
        """
        Raises:
           InvalidOrderIdError
           InsufficientExpectednessError
        """
