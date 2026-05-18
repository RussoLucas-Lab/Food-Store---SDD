"""
Configuración de la base de datos PostgreSQL.

Provee:
- engine: SQLAlchemy engine síncrono conectado a PostgreSQL via DATABASE_URL
- get_db(): generador de sesión por request (para FastAPI Depends)
- create_all_tables(): fallback para crear tablas si Alembic no está disponible
"""

import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
from pathlib import Path

# Cargar .env desde la raíz del proyecto
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env", override=True)

def _build_database_url() -> str:
    """
    Construir DATABASE_URL desde variable directa o desde componentes individuales.

    Prioridad:
    1. DATABASE_URL (si está definida directamente)
    2. DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME (componentes individuales)
    3. Default local para desarrollo
    """
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "postgres")
    dbname = os.getenv("DB_NAME", "foodstore_db")

    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


DATABASE_URL = _build_database_url()

# Engine síncrono — sin async para mantener compatibilidad con routers existentes
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("ENV", "development") == "development",
    pool_pre_ping=True,  # verifica que la conexión siga activa antes de usar
)


def get_db():
    """
    Generador de sesión SQLModel por request.

    Uso en routers FastAPI:
        session: Session = Depends(get_db)

    La sesión se cierra automáticamente al salir del contexto,
    haciendo rollback si no se hizo commit explícito.
    """
    with Session(engine) as session:
        yield session


def create_all_tables() -> None:
    """
    Crear todas las tablas registradas en SQLModel.metadata.

    Solo se usa como fallback cuando Alembic no está disponible
    (p. ej. en tests o en desarrollo sin migraciones configuradas).
    En producción, usar `alembic upgrade head`.
    """
    # Importar todos los modelos SQLModel para que se registren en metadata
    from backend.modules.auth.sqlmodel_model import UsuarioDB  # noqa: F401
    from backend.modules.categorias.sqlmodel_model import CategoriDB  # noqa: F401
    from backend.modules.ingredientes.sqlmodel_model import IngredienteDB  # noqa: F401
    from backend.modules.productos.sqlmodel_model import ProductoDB, ProductoCategoriaDB  # noqa: F401
    from backend.modules.clientes.sqlmodel_model import ClienteDB  # noqa: F401
    from backend.modules.direcciones.sqlmodel_model import DireccionEntregaDB  # noqa: F401
    from backend.modules.pedidos.sqlmodel_model import PedidoDB, DetallePedidoDB, HistorialEstadoPedidoDB  # noqa: F401
    from backend.modules.pagos.sqlmodel_model import PagoDB  # noqa: F401

    SQLModel.metadata.create_all(engine)
