from models.identifiers import OrderId
from models.order import OrderStatus, OrderPreSave, OrderItem
from ports.api.place_order_use_case import PlaceOrderUseCase
from ports.api.update_order_status_use_case import UpdateOrderStatusUseCase
from ports.spi.get_or_create_customer_by_customer_id_port import (
    GetOrCreateCustomerByCustomerIdPort,
)
from ports.spi.dispatch_orders_message_port import DispatchOrderUpdateMessagePort
from ports.spi.save_order_port import SaveOrderPort
from ports.spi.get_current_product_versions_by_product_ids import (
    GetCurrentProductVersionsByProductIdsPort,
)
from ports.spi.save_new_order_status_port import SaveNewOrderStatusPort


class OrdersService(PlaceOrderUseCase, UpdateOrderStatusUseCase):
    _dispatch_order_update_message_port: DispatchOrderUpdateMessagePort
    _save_order_port: SaveOrderPort
    _get_current_product_versions_by_product_ids_port: GetCurrentProductVersionsByProductIdsPort
    _get_or_create_customer_by_customer_id_port: GetOrCreateCustomerByCustomerIdPort
    _save_new_order_status_port: SaveNewOrderStatusPort

    def __init__(
        self,
        dispatch_order_update_message_port: DispatchOrderUpdateMessagePort,
        save_order_port: SaveOrderPort,
        get_current_product_versions_by_product_ids_port: GetCurrentProductVersionsByProductIdsPort,
        get_or_create_customer_by_customer_id_port: GetOrCreateCustomerByCustomerIdPort,
        save_new_order_status_port: SaveNewOrderStatusPort,
    ) -> None:
        self._dispatch_order_update_message_port = dispatch_order_update_message_port
        self._save_order_port = save_order_port
        self._get_current_product_version_by_product_ids_port = (
            get_current_product_versions_by_product_ids_port
        )
        self._get_or_create_customer_by_customer_id_port = (
            get_or_create_customer_by_customer_id_port
        )
        self._save_new_order_status_port = save_new_order_status_port

    def place_order(
        self, command: PlaceOrderUseCase.PlaceOrderCommand
    ) -> PlaceOrderUseCase.PlaceOrderResult:
        product_ids = [item.product_id for item in command.items]
        product_versions_result = self._get_current_product_version_by_product_ids_port.get_current_product_versions_by_product_ids(
            product_ids=product_ids
        )
        if (
            type(product_versions_result)
            == GetCurrentProductVersionsByProductIdsPort.ProductVersionsNotFoundResult
        ):
            return PlaceOrderUseCase.InvalidProductResult(
                product_id=product_versions_result.product_ids_not_found[0]
            )
        assert (
            type(product_versions_result)
            == GetCurrentProductVersionsByProductIdsPort.SuccessfullyFoundProductVersions
        )
        product_versions = product_versions_result.product_versions
        assert len(product_versions) == len(command.items)
        order_items: list[OrderItem] = [
            OrderItem(product_version=product_versions[i], quantity=item.quantity)
            for i, item in enumerate(command.items)
        ]
        customer_result = self._get_or_create_customer_by_customer_id_port.get_or_create_customer_by_customer_id(
            customer_id=command.customer_id
        )
        assert (
            type(customer_result)
            == GetOrCreateCustomerByCustomerIdPort.SuccessfullyGotOrCreatedCustomerByIdResult
        )

        order_pre_save = OrderPreSave(
            customer_id=customer_result.customer.id,
            address=command.address,
            items=order_items,
        )

        save_order_result = self._save_order_port.save_order(
            order_pre_save=order_pre_save
        )
        if save_order_result == SaveOrderPort.FailedToSaveOrder:
            return PlaceOrderUseCase.FailedToSaveOrderResult()
        assert type(save_order_result) == SaveOrderPort.SuccessfullySavedOrder
        self._dispatch_order_update_message_port.dispatch_order_update_message(
            message=DispatchOrderUpdateMessagePort.OrderUpdateMessage(
                order=save_order_result
            )
        )
        return PlaceOrderUseCase.SuccessfullyPlacedOrderResult()

    def update_order_status(
        self, order_id: OrderId, new_status: OrderStatus
    ) -> UpdateOrderStatusUseCase.UpdateOrderStatusResult:
        save_new_order_status_result = (
            self._save_new_order_status_port.save_new_order_status(
                order_id=order_id, new_status=new_status
            )
        )
        if (
            type(save_new_order_status_result)
            == SaveNewOrderStatusPort.OrderIdNotFoundResult
        ):
            return UpdateOrderStatusUseCase.OrderIdNotFoundResult()
        assert (
            type(save_new_order_status_result)
            == SaveNewOrderStatusPort.SuccessfullySavedNewOrderStatusResult
        )
        self._dispatch_order_update_message_port.dispatch_order_update_message(
            message=DispatchOrderUpdateMessagePort.OrderUpdateMessage(
                order=save_new_order_status_result.new_order
            )
        )
        return UpdateOrderStatusUseCase.SuccessfullyUpdatedOrderStatusResult()
