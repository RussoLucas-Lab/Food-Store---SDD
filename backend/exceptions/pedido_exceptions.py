"""
Excepciones personalizadas para Pedidos.
"""


class CartEmptyError(Exception):
    """Excepción cuando se intenta crear pedido con carrito vacío"""
    def __init__(self, message: str = "El carrito está vacío"):
        self.message = message
        super().__init__(self.message)


class StockInsufficient(Exception):
    """Excepción cuando no hay stock suficiente de un producto"""
    def __init__(self, message: str = "Stock insuficiente"):
        self.message = message
        super().__init__(self.message)


class PedidoNotFound(Exception):
    """Excepción cuando no se encuentra un pedido"""
    def __init__(self, pedido_id: int):
        self.message = f"Pedido {pedido_id} no encontrado"
        super().__init__(self.message)


class UnauthorizedPedidoAccess(Exception):
    """Excepción cuando un usuario intenta acceder a un pedido que no le pertenece"""
    def __init__(self, message: str = "No autorizado para acceder a este pedido"):
        self.message = message
        super().__init__(self.message)


class DireccionNotFound(Exception):
    """Excepción cuando no se encuentra una dirección"""
    def __init__(self, direccion_id: int):
        self.message = f"Dirección {direccion_id} no encontrada"
        super().__init__(self.message)
