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


class TransicionInvalida(Exception):
    """
    Excepción cuando se intenta una transición de estado no permitida por la FSM.

    Cubre:
    - Saltos de estado (e.g. CONFIRMADO → EN_CAMINO)
    - Retrocesos (e.g. EN_CAMINO → EN_PREPARACION)
    - Transición desde estado terminal (ENTREGADO, CANCELADO)
    - Intento manual de PENDIENTE → CONFIRMADO (exclusiva del sistema)
    """
    def __init__(self, estado_actual: str, estado_destino: str):
        self.message = (
            f"Transición inválida: '{estado_actual}' → '{estado_destino}'. "
            "Verifique el mapa de transiciones permitidas."
        )
        super().__init__(self.message)


class RolNoAutorizadoParaTransicion(Exception):
    """
    Excepción cuando el rol del usuario no está autorizado para ejecutar
    la transición de estado solicitada.

    Cubre:
    - Cliente intenta avanzar un pedido que no puede avanzar
    - PEDIDOS intenta cancelar desde EN_PREPARACION (solo ADMIN)
    - Cliente intenta cancelar un pedido ajeno
    """
    def __init__(self, rol: str, estado_actual: str, estado_destino: str):
        self.message = (
            f"El rol '{rol}' no está autorizado para la transición "
            f"'{estado_actual}' → '{estado_destino}'."
        )
        super().__init__(self.message)
