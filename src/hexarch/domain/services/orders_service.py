from models.order import OrderId, OrderStatus
from ports.api.place_order_use_case import PlaceOrderUseCase
from ports.api.update_order_status_use_case import UpdateOrderStatusUseCase
from ports.spi.dispatch_orders_message_port import DispatchOrderUpdateMessagePort
from ports.spi.save_order_port import SaveOrderPort
from ports.spi.get_products_by_product_ids_port import GetProductsByProductIdsPort


class OrdersService(PlaceOrderUseCase, UpdateOrderStatusUseCase):
    _dispatch_order_update_message_port: DispatchOrderUpdateMessagePort
    _save_order_port: SaveOrderPort
    _get_products_by_product_ids_port: GetProductsByProductIdsPort

    def __init__(
        self,
        dispatch_order_update_message_port: DispatchOrderUpdateMessagePort,
        save_order_port: SaveOrderPort,
        get_products_by_product_ids_port: GetProductsByProductIdsPort,
    ) -> None:
        self._dispatch_order_update_message_port = dispatch_order_update_message_port
        self._save_order_port = save_order_port
        self._get_products_by_product_ids_port = get_products_by_product_ids_port

    def place_order(
        self, command: PlaceOrderUseCase.PlaceOrderCommand
    ) -> PlaceOrderUseCase.PlaceOrderResult:
        pass

    def update_order_status(
        self, order_id: OrderId, new_status: OrderStatus
    ) -> UpdateOrderStatusUseCase.UpdateOrderStatusResult:
        pass
