from backend.core.uow import IUnitOfWork
from backend.modules.auth.repository import InMemoryUsuarioRepository
from backend.modules.categorias.repository import InMemoryCategoriaRepository
from backend.modules.ingredientes.repository import InMemoryIngredienteRepository
from backend.modules.productos.repository import InMemoryProductRepository, InMemoryProductIngredientRepository
from backend.modules.clientes.repository import InMemoryClienteRepository
from backend.modules.pedidos.repository import (
    InMemoryPedidoRepository,
    InMemoryDetallePedidoRepository,
    InMemoryHistorialEstadoPedidoRepository,
)
from backend.modules.direcciones.repository import InMemoryDireccionRepository
from backend.modules.pagos.repository import InMemoryPagoRepository

class InMemoryUnitOfWork(IUnitOfWork):
    def __init__(self):
        self._repositories = {}
        self._usuarios = InMemoryUsuarioRepository()
        self._categorias = InMemoryCategoriaRepository()
        self._ingredientes = InMemoryIngredienteRepository()
        self._productos = InMemoryProductRepository()
        self._product_ingredients = InMemoryProductIngredientRepository()
        self._clientes = InMemoryClienteRepository()
        self._pedidos = InMemoryPedidoRepository()
        self._detalles_pedido = InMemoryDetallePedidoRepository()
        self._historial_estado = InMemoryHistorialEstadoPedidoRepository()
        self._direcciones = InMemoryDireccionRepository()
        self._pagos = InMemoryPagoRepository()
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.committed = False

    @property
    def repositories(self):
        return self._repositories

    @property
    def usuarios(self):
        """Repositorio de usuarios"""
        return self._usuarios

    @property
    def categorias(self):
        """Repositorio de categorías"""
        return self._categorias

    @property
    def ingredientes(self):
        """Repositorio de ingredientes"""
        return self._ingredientes

    @property
    def productos(self):
        """Repositorio de productos"""
        return self._productos

    @property
    def product_ingredients(self):
        """Repositorio de relaciones producto-ingrediente"""
        return self._product_ingredients

    @property
    def clientes(self):
        """Repositorio de clientes"""
        return self._clientes

    @property
    def pedidos(self):
        """Repositorio de pedidos"""
        return self._pedidos

    @property
    def detalles_pedido(self):
        """Repositorio de detalles de pedido"""
        return self._detalles_pedido

    @property
    def historial_estado(self):
        """Repositorio de historial de estado de pedido (append-only)"""
        return self._historial_estado

    @property
    def direcciones(self):
        """Repositorio de direcciones de entrega"""
        return self._direcciones

    @property
    def pagos(self):
        """Repositorio de pagos (MercadoPago)"""
        return self._pagos


# ── Singleton UoW ─────────────────────────────────────────────────────────────
# Instancia compartida por todos los routers que necesitan acceso consistente
# al mismo almacenamiento en memoria (p. ej. pedidos y direcciones).
# Los routers deben importar esta instancia en lugar de crear una nueva.
singleton_uow = InMemoryUnitOfWork()
