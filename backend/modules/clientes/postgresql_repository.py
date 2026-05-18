"""
Implementación PostgreSQL de IClienteRepository usando SQLModel Session.
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from .repository import IClienteRepository
from .model import Cliente
from .sqlmodel_model import ClienteDB


def _to_domain(db_obj: ClienteDB) -> Cliente:
    """Convertir ClienteDB → Cliente (dominio)."""
    return Cliente(
        id=db_obj.id,
        nombre=db_obj.nombre,
        email=db_obj.email,
        telefono=db_obj.telefono,
        direccion=db_obj.direccion,
        activo=db_obj.activo,
        user_id=db_obj.user_id,
        created_at=db_obj.created_at,
        updated_at=db_obj.updated_at,
    )


class PostgreSQLClienteRepository(IClienteRepository):
    """Implementación PostgreSQL de IClienteRepository."""

    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        nombre: str,
        email: str,
        direccion: str,
        telefono: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Cliente:
        """Crear nuevo cliente."""
        existing = self._session.exec(
            select(ClienteDB).where(ClienteDB.email == email.lower())
        ).first()
        if existing:
            raise ValueError(f"Email '{email}' ya está registrado")

        now = datetime.utcnow()
        db_obj = ClienteDB(
            nombre=nombre,
            email=email.lower(),
            telefono=telefono,
            direccion=direccion,
            activo=True,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_domain(db_obj)

    def find_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """Buscar cliente por id (solo activos)."""
        db_obj = self._session.exec(
            select(ClienteDB).where(
                ClienteDB.id == cliente_id,
                ClienteDB.activo == True,  # noqa: E712
            )
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def find_by_email(self, email: str) -> Optional[Cliente]:
        """Buscar cliente por email (solo activos)."""
        db_obj = self._session.exec(
            select(ClienteDB).where(
                ClienteDB.email == email.lower(),
                ClienteDB.activo == True,  # noqa: E712
            )
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def get_all_active(
        self,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "id",
    ) -> List[Cliente]:
        """Listar clientes activos con paginación."""
        stmt = select(ClienteDB).where(ClienteDB.activo == True)  # noqa: E712

        if sort_by == "nombre":
            stmt = stmt.order_by(ClienteDB.nombre)
        elif sort_by == "created_at":
            stmt = stmt.order_by(ClienteDB.created_at.desc())
        else:
            stmt = stmt.order_by(ClienteDB.id)

        stmt = stmt.offset(skip).limit(limit)
        db_objs = self._session.exec(stmt).all()
        return [_to_domain(obj) for obj in db_objs]

    def search(self, query: str, skip: int = 0, limit: int = 20) -> List[Cliente]:
        """Buscar clientes por nombre o email."""
        q = f"%{query.lower()}%"
        stmt = (
            select(ClienteDB)
            .where(
                ClienteDB.activo == True,  # noqa: E712
            )
            .filter(
                (ClienteDB.nombre.ilike(q)) | (ClienteDB.email.ilike(q))
            )
            .offset(skip)
            .limit(limit)
        )
        db_objs = self._session.exec(stmt).all()
        return [_to_domain(obj) for obj in db_objs]

    def update(
        self,
        cliente_id: int,
        nombre: str = None,
        email: str = None,
        telefono: Optional[str] = None,
        direccion: str = None,
    ) -> Optional[Cliente]:
        """Actualizar cliente existente."""
        db_obj = self._session.get(ClienteDB, cliente_id)
        if not db_obj:
            return None

        if email is not None and email.lower() != db_obj.email:
            conflict = self._session.exec(
                select(ClienteDB).where(ClienteDB.email == email.lower())
            ).first()
            if conflict:
                raise ValueError(f"Email '{email}' ya está registrado")
            db_obj.email = email.lower()

        if nombre is not None:
            db_obj.nombre = nombre
        if telefono is not None:
            db_obj.telefono = telefono
        if direccion is not None:
            db_obj.direccion = direccion

        db_obj.updated_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_domain(db_obj)

    def soft_delete(self, cliente_id: int) -> bool:
        """Marcar cliente como inactivo (soft delete)."""
        db_obj = self._session.get(ClienteDB, cliente_id)
        if not db_obj:
            return False
        db_obj.activo = False
        db_obj.updated_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        return True

    def reactivate(self, cliente_id: int) -> Optional[Cliente]:
        """Reactivar cliente inactivo."""
        db_obj = self._session.get(ClienteDB, cliente_id)
        if not db_obj:
            return None
        db_obj.activo = True
        db_obj.updated_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_domain(db_obj)

    def find_all(self, include_inactive: bool = False) -> List[Cliente]:
        """Obtener todos los clientes."""
        stmt = select(ClienteDB).order_by(ClienteDB.id)
        if not include_inactive:
            stmt = stmt.where(ClienteDB.activo == True)  # noqa: E712
        db_objs = self._session.exec(stmt).all()
        return [_to_domain(obj) for obj in db_objs]
