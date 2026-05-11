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
from .routers.auth import router as auth_router
from .routers.categorias import router as categorias_router
from .routers.ingredientes import router as ingredientes_router
from .routers.productos import router as productos_router
from .routers.clientes import router as clientes_router

# Cargar variables de entorno
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env', override=True)

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)

# Crear aplicación FastAPI
app = FastAPI(
    title="Food Store API",
    description="Backend API para sistema de gestión de comidas",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
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
app.include_router(categorias_router)
app.include_router(ingredientes_router)
app.include_router(productos_router)
app.include_router(clientes_router)

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

