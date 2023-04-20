from typing import Protocol
from models.order import VersionedOrder, PersistedOrder


class PersistOrderPort(Protocol):
    def persist_order(self, versioned_order: VersionedOrder) -> PersistedOrder:
        pass
