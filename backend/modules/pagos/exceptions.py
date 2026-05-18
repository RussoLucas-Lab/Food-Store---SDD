"""
Excepciones personalizadas para el módulo Pagos.
"""


class PedidoNotPendiente(Exception):
    """
    Excepción cuando se intenta pagar un pedido que no está en estado PENDIENTE.

    HTTP 400 Bad Request.
    """

    def __init__(self, pedido_id: int, estado_actual: str):
        self.message = (
            f"El pedido {pedido_id} no está en estado PENDIENTE "
            f"(estado actual: {estado_actual}). Solo se pueden pagar pedidos PENDIENTES."
        )
        super().__init__(self.message)


class PedidoNotFound(Exception):
    """
    Excepción cuando el pedido no existe o no pertenece al cliente.

    HTTP 404 Not Found.
    """

    def __init__(self, pedido_id: int):
        self.message = f"Pedido {pedido_id} no encontrado o no autorizado."
        super().__init__(self.message)


class PagoAlreadyExists(Exception):
    """
    Excepción cuando ya existe un pago para el pedido (idempotencia).

    HTTP 200 OK — retorna el pago existente sin duplicar.
    """

    def __init__(self, pedido_id: int):
        self.message = f"Ya existe un pago para el pedido {pedido_id}."
        super().__init__(self.message)


class MercadoPagoError(Exception):
    """
    Excepción cuando falla la comunicación con MercadoPago SDK.

    HTTP 502 Bad Gateway.
    """

    def __init__(self, detail: str = "Error al procesar el pago con MercadoPago"):
        self.message = detail
        super().__init__(self.message)
