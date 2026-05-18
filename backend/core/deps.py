"""
Dependencias FastAPI para inyección de UoW por request.

Uso en routers:
    from backend.core.deps import get_uow
    from backend.core.uow_postgresql import PostgreSQLUnitOfWork

    @router.get("/")
    def my_endpoint(uow: PostgreSQLUnitOfWork = Depends(get_uow)):
        ...
"""

from fastapi import Depends
from sqlmodel import Session

from backend.core.database import get_db
from backend.core.uow_postgresql import PostgreSQLUnitOfWork


def get_uow(session: Session = Depends(get_db)) -> PostgreSQLUnitOfWork:
    """
    Proveer un PostgreSQLUnitOfWork con sesión de BD por request.

    Cada request recibe su propia sesión (inyectada por get_db),
    garantizando aislamiento transaccional entre requests concurrentes.
    """
    return PostgreSQLUnitOfWork(session)
