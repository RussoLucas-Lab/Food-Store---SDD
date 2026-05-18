"""
PostgreSQLUnitOfWork — implementación de IUnitOfWork para PostgreSQL.

Recibe una Session SQLAlchemy por request (inyectada via Depends(get_db))
y expone todos los repositorios PostgreSQL. El commit/rollback se gestiona
por la sesión — el UoW delega a la sesión subyacente.
"""

from sqlmodel import Session

from backend.core.uow import IUnitOfWork
from backend.modules.auth.postgresql_repository import PostgreSQLUsuarioRepository
from backend.modules.categorias.postgresql_repository import PostgreSQLCategoriaRepository
from backend.modules.ingredientes.postgresql_repository import PostgreSQLIngredienteRepository
from backend.modules.productos.postgresql_repository import (
    PostgreSQLProductRepository,
    PostgreSQLProductIngredientRepository,
)
from backend.modules.clientes.postgresql_repository import PostgreSQLClienteRepository
from backend.modules.direcciones.postgresql_repository import PostgreSQLDireccionRepository
from backend.modules.pedidos.postgresql_repository import (
    PostgreSQLPedidoRepository,
    PostgreSQLDetallePedidoRepository,
    PostgreSQLHistorialEstadoPedidoRepository,
)
from backend.modules.pagos.postgresql_repository import PostgreSQLPagoRepository


class PostgreSQLUnitOfWork(IUnitOfWork):
    """
    Unit of Work que usa una sesión SQLAlchemy por request.

    Cada request obtiene su propia sesión via Depends(get_db),
    garantizando aislamiento transaccional entre requests concurrentes.
    """

    def __init__(self, session: Session):
        self._session = session
        self._usuarios = PostgreSQLUsuarioRepository(session)
        self._categorias = PostgreSQLCategoriaRepository(session)
        self._ingredientes = PostgreSQLIngredienteRepository(session)
        self._productos = PostgreSQLProductRepository(session)
        self._product_ingredients = PostgreSQLProductIngredientRepository(session)
        self._clientes = PostgreSQLClienteRepository(session)
        self._direcciones = PostgreSQLDireccionRepository(session)
        self._pedidos = PostgreSQLPedidoRepository(session)
        self._detalles_pedido = PostgreSQLDetallePedidoRepository(session)
        self._historial_estado = PostgreSQLHistorialEstadoPedidoRepository(session)
        self._pagos = PostgreSQLPagoRepository(session)

    def commit(self) -> None:
        """Persistir todos los cambios de la sesión en PostgreSQL."""
        self._session.commit()

    def rollback(self) -> None:
        """Deshacer todos los cambios no commitados de la sesión."""
        self._session.rollback()

    @property
    def repositories(self):
        return {}

    @property
    def usuarios(self):
        return self._usuarios

    @property
    def categorias(self):
        return self._categorias

    @property
    def ingredientes(self):
        return self._ingredientes

    @property
    def productos(self):
        return self._productos

    @property
    def product_ingredients(self):
        return self._product_ingredients

    @property
    def clientes(self):
        return self._clientes

    @property
    def pedidos(self):
        return self._pedidos

    @property
    def detalles_pedido(self):
        return self._detalles_pedido

    @property
    def historial_estado(self):
        return self._historial_estado

    @property
    def direcciones(self):
        return self._direcciones

    @property
    def pagos(self):
        return self._pagos
