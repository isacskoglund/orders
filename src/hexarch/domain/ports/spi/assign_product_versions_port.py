from typing import Protocol
from models.order import RequestedOrder, VersionedOrder


class AssignProductVersionsPort(Protocol):
    def assign_product_versions(
        self, requested_order: RequestedOrder
    ) -> VersionedOrder:
        """
        Raises:
            InvalidProductIdError: Product was not found.
            NoCurrentProductVersionError: Product has no current version.
        """
        pass
