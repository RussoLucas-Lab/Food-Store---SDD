"""
Alembic env.py — configurado para Food Store con SQLModel y PostgreSQL.

Importa todos los modelos SQLModel para que Alembic pueda detectar las tablas
al usar --autogenerate. Usa DATABASE_URL del entorno (o construida desde
DB_HOST/DB_PORT/DB_USER/DB_PASS/DB_NAME).
"""

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel
from alembic import context

# ── Agregar la raíz del proyecto al sys.path para poder importar backend.* ───
# La raíz es el directorio padre del directorio `alembic/`
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Cargar variables de entorno desde .env en la raíz del proyecto
from dotenv import load_dotenv
load_dotenv(dotenv_path=ROOT_DIR / ".env", override=True)

# ── Importar TODOS los modelos SQLModel para que se registren en metadata ─────
# Importante: si se omite algún modelo, Alembic no lo detectará con --autogenerate
from backend.modules.auth.sqlmodel_model import UsuarioDB  # noqa: F401
from backend.modules.categorias.sqlmodel_model import CategoriDB  # noqa: F401
from backend.modules.ingredientes.sqlmodel_model import IngredienteDB  # noqa: F401
from backend.modules.productos.sqlmodel_model import ProductoDB, ProductoCategoriaDB, ProductoIngredienteDB  # noqa: F401
from backend.modules.clientes.sqlmodel_model import ClienteDB  # noqa: F401
from backend.modules.direcciones.sqlmodel_model import DireccionEntregaDB  # noqa: F401
from backend.modules.pedidos.sqlmodel_model import PedidoDB, DetallePedidoDB, HistorialEstadoPedidoDB  # noqa: F401
from backend.modules.pagos.sqlmodel_model import PagoDB  # noqa: F401

# ── Alembic config ─────────────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLModel.metadata contiene todas las tablas importadas arriba
target_metadata = SQLModel.metadata


# ── Helper para construir DATABASE_URL ────────────────────────────────────────

def _get_url() -> str:
    """
    Obtener DATABASE_URL desde variable directa o desde componentes individuales.
    Tiene precedencia sobre el valor en alembic.ini.
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


# ── Migrations ─────────────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (sin conexión activa)."""
    url = _get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (con engine y conexión activa)."""
    # Override el sqlalchemy.url con el valor del entorno
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
