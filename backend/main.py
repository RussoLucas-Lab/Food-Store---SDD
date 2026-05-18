from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from dotenv import load_dotenv
from pathlib import Path

# Importar routers
from .modules.auth.router import router as auth_router
from .modules.categorias.router import router as categorias_router
from .modules.ingredientes.router import router as ingredientes_router
from .modules.productos.router import router as productos_router
from .modules.clientes.router import router as clientes_router
from .modules.pedidos.router import router as pedidos_router
from .modules.direcciones.router import router as direcciones_router
from .modules.pagos.router import router as pagos_router
from .modules.admin.router import router as admin_router

# Cargar variables de entorno
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env', override=True)

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Aplicar migraciones de Alembic (o crear tablas como fallback)
    try:
        from alembic.config import Config
        from alembic import command
        from pathlib import Path as _Path
        alembic_cfg = Config(str(_Path(__file__).parent.parent / "alembic.ini"))
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(
            f"Alembic upgrade failed ({e}), falling back to create_all_tables()"
        )
        from .core.database import create_all_tables
        create_all_tables()

    # 2. Seed de datos iniciales (idempotente)
    from .db.seed import seed_initial_data
    seed_initial_data()
    yield


# Crear aplicación FastAPI
app = FastAPI(
    title="Food Store API",
    description="Backend API para sistema de gestión de comidas",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Aplicar rate limiter
app.state.limiter = limiter

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador de errores de rate limiting
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded: 5 attempts per 15 minutes"}
    )

# ============================================================================
# Registrar routers
# ============================================================================

app.include_router(auth_router)
app.include_router(categorias_router, prefix="/api/v1")
app.include_router(ingredientes_router, prefix="/api/v1")
app.include_router(productos_router, prefix="/api/v1")
app.include_router(clientes_router, prefix="/api/v1")
app.include_router(pedidos_router, prefix="/api/v1")
app.include_router(direcciones_router, prefix="/api/v1")
app.include_router(pagos_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1/admin")

# ============================================================================
# Endpoints públicos
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "environment": os.getenv("ENV", "development"),
        "app": "Food Store API"
    }

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint con información de la API"""
    return {
        "app": "Food Store API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENV") == "development"
    )

