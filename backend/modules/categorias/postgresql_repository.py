"""
Implementación PostgreSQL de ICategoriaRepository usando SQLModel Session.
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from .repository import ICategoriaRepository
from .model import Categoria
from .sqlmodel_model import CategoriDB


def _to_domain(db_obj: CategoriDB) -> Categoria:
    """Convertir CategoriDB → Categoria (dominio)."""
    return Categoria(
        id=db_obj.id,
        nombre=db_obj.nombre,
        descripcion=db_obj.descripcion,
        is_active=db_obj.is_active,
        created_at=db_obj.created_at,
        updated_at=db_obj.updated_at,
        deleted_at=db_obj.deleted_at,
    )


class PostgreSQLCategoriaRepository(ICategoriaRepository):
    """Implementación PostgreSQL de ICategoriaRepository."""

    def __init__(self, session: Session):
        self._session = session

    def create(self, nombre: str, descripcion: str = "") -> Categoria:
        """Crear nueva categoría."""
        existing = self._session.exec(
            select(CategoriDB).where(CategoriDB.nombre == nombre)
        ).first()
        if existing:
            raise ValueError(f"Categoría '{nombre}' ya existe")

        now = datetime.utcnow()
        db_obj = CategoriDB(
            nombre=nombre,
            descripcion=descripcion,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_domain(db_obj)

    def find_by_id(self, categoria_id: int) -> Optional[Categoria]:
        """Buscar categoría por id (solo activas)."""
        db_obj = self._session.exec(
            select(CategoriDB).where(
                CategoriDB.id == categoria_id,
                CategoriDB.is_active == True,  # noqa: E712
            )
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def find_by_name(self, nombre: str) -> Optional[Categoria]:
        """Buscar categoría por nombre (solo activas)."""
        db_obj = self._session.exec(
            select(CategoriDB).where(
                CategoriDB.nombre == nombre,
                CategoriDB.is_active == True,  # noqa: E712
            )
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def list_active(
        self,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "id",
        include_inactive: bool = False,
    ) -> List[Categoria]:
        """Listar categorías con paginación y ordenamiento."""
        stmt = select(CategoriDB)
        if not include_inactive:
            stmt = stmt.where(CategoriDB.is_active == True)  # noqa: E712

        if sort_by == "nombre":
            stmt = stmt.order_by(CategoriDB.nombre)
        elif sort_by == "created_at":
            stmt = stmt.order_by(CategoriDB.created_at.desc())
        else:
            stmt = stmt.order_by(CategoriDB.id)

        stmt = stmt.offset(skip).limit(limit)
        db_objs = self._session.exec(stmt).all()
        return [_to_domain(obj) for obj in db_objs]

    def update(
        self,
        categoria_id: int,
        nombre: str = None,
        descripcion: str = None,
    ) -> Optional[Categoria]:
        """Actualizar categoría existente."""
        db_obj = self._session.get(CategoriDB, categoria_id)
        if not db_obj:
            return None

        if nombre is not None and nombre != db_obj.nombre:
            # Verificar unicidad del nuevo nombre
            conflict = self._session.exec(
                select(CategoriDB).where(CategoriDB.nombre == nombre)
            ).first()
            if conflict:
                raise ValueError(f"Categoría '{nombre}' ya existe")
            db_obj.nombre = nombre

        if descripcion is not None:
            db_obj.descripcion = descripcion

        db_obj.updated_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_domain(db_obj)

    def soft_delete(self, categoria_id: int) -> bool:
        """Marcar categoría como inactiva (soft delete) — idempotente."""
        db_obj = self._session.get(CategoriDB, categoria_id)
        if not db_obj:
            return False

        if db_obj.is_active:
            now = datetime.utcnow()
            db_obj.is_active = False
            db_obj.deleted_at = now
            db_obj.updated_at = now
            self._session.add(db_obj)
            self._session.flush()

        return True

    def find_all(self, include_inactive: bool = False) -> List[Categoria]:
        """Obtener todas las categorías (activas o todas)."""
        stmt = select(CategoriDB).order_by(CategoriDB.id)
        if not include_inactive:
            stmt = stmt.where(CategoriDB.is_active == True)  # noqa: E712
        db_objs = self._session.exec(stmt).all()
        return [_to_domain(obj) for obj in db_objs]
