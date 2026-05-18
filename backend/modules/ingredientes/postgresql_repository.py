"""
Implementación PostgreSQL de IIngredienteRepository usando SQLModel Session.
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from .repository import IIngredienteRepository
from .model import Ingrediente, UnidadMedida
from .sqlmodel_model import IngredienteDB


def _to_domain(db_obj: IngredienteDB) -> Ingrediente:
    """Convertir IngredienteDB → Ingrediente (dominio)."""
    return Ingrediente(
        id=db_obj.id,
        nombre=db_obj.nombre,
        descripcion=db_obj.descripcion,
        unidad_medida=db_obj.unidad_medida,
        cantidad_stock=db_obj.cantidad_stock,
        cantidad_minima=db_obj.cantidad_minima,
        cantidad_reservada=db_obj.cantidad_reservada,
        categoria_id=db_obj.categoria_id,
        is_active=db_obj.is_active,
        created_at=db_obj.created_at,
        updated_at=db_obj.updated_at,
        deleted_at=db_obj.deleted_at,
    )


class PostgreSQLIngredienteRepository(IIngredienteRepository):
    """Implementación PostgreSQL de IIngredienteRepository."""

    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        nombre: str,
        unidad_medida: str,
        cantidad_stock: int,
        cantidad_minima: int,
        descripcion: str = "",
        categoria_id: Optional[int] = None,
    ) -> Ingrediente:
        """Crear nuevo ingrediente."""
        existing = self._session.exec(
            select(IngredienteDB).where(IngredienteDB.nombre == nombre)
        ).first()
        if existing:
            raise ValueError(f"Ingrediente '{nombre}' ya existe")

        try:
            UnidadMedida(unidad_medida)
        except ValueError:
            raise ValueError(f"Unidad de medida '{unidad_medida}' inválida")

        now = datetime.utcnow()
        db_obj = IngredienteDB(
            nombre=nombre,
            descripcion=descripcion,
            unidad_medida=unidad_medida,
            cantidad_stock=cantidad_stock,
            cantidad_minima=cantidad_minima,
            cantidad_reservada=0,
            categoria_id=categoria_id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_domain(db_obj)

    def find_by_id(self, ingrediente_id: int) -> Optional[Ingrediente]:
        """Buscar ingrediente por id (solo activos)."""
        db_obj = self._session.exec(
            select(IngredienteDB).where(
                IngredienteDB.id == ingrediente_id,
                IngredienteDB.is_active == True,  # noqa: E712
            )
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def find_by_name(self, nombre: str) -> Optional[Ingrediente]:
        """Buscar ingrediente por nombre (solo activos)."""
        db_obj = self._session.exec(
            select(IngredienteDB).where(
                IngredienteDB.nombre == nombre,
                IngredienteDB.is_active == True,  # noqa: E712
            )
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def list_active(
        self,
        skip: int = 0,
        limit: int = 20,
        categoria_id: Optional[int] = None,
        disponibles_solo: bool = False,
        alerta_stock_bajo: bool = False,
        unidad_medida: Optional[str] = None,
        ordenar_por: str = "id",
        orden: str = "asc",
    ) -> List[Ingrediente]:
        """Listar ingredientes con paginación y filtros."""
        stmt = select(IngredienteDB).where(IngredienteDB.is_active == True)  # noqa: E712

        if categoria_id is not None:
            stmt = stmt.where(IngredienteDB.categoria_id == categoria_id)
        if unidad_medida:
            stmt = stmt.where(IngredienteDB.unidad_medida == unidad_medida)

        # Ordenamiento
        reverse = orden.lower() == "desc"
        if ordenar_por == "nombre":
            col = IngredienteDB.nombre
        elif ordenar_por == "cantidad_stock":
            col = IngredienteDB.cantidad_stock
        elif ordenar_por == "created_at":
            col = IngredienteDB.created_at
        else:
            col = IngredienteDB.id

        stmt = stmt.order_by(col.desc() if reverse else col.asc())
        stmt = stmt.offset(skip).limit(limit)

        db_objs = self._session.exec(stmt).all()
        ingredientes = [_to_domain(obj) for obj in db_objs]

        # Filtros post-query (requieren cálculo en Python)
        if disponibles_solo:
            ingredientes = [i for i in ingredientes if i.stock_disponible > 0]
        if alerta_stock_bajo:
            ingredientes = [i for i in ingredientes if i.alerta_stock_bajo]

        return ingredientes

    def buscar_por_nombre(self, q: str, skip: int = 0, limit: int = 20) -> List[Ingrediente]:
        """Buscar ingredientes por nombre (parcial, case-insensitive)."""
        stmt = (
            select(IngredienteDB)
            .where(
                IngredienteDB.is_active == True,  # noqa: E712
                IngredienteDB.nombre.ilike(f"%{q}%"),
            )
            .order_by(IngredienteDB.nombre)
            .offset(skip)
            .limit(limit)
        )
        db_objs = self._session.exec(stmt).all()
        return [_to_domain(obj) for obj in db_objs]

    def update(
        self,
        ingrediente_id: int,
        nombre: str = None,
        descripcion: str = None,
        cantidad_stock: int = None,
        cantidad_minima: int = None,
    ) -> Optional[Ingrediente]:
        """Actualizar ingrediente existente."""
        # Soporte de pasar un objeto Ingrediente directamente (compatibilidad con tests)
        if isinstance(ingrediente_id, Ingrediente):
            ing_obj = ingrediente_id
            db_obj = self._session.get(IngredienteDB, ing_obj.id)
            if not db_obj:
                return None
            db_obj.nombre = ing_obj.nombre
            db_obj.descripcion = ing_obj.descripcion
            db_obj.cantidad_stock = ing_obj.cantidad_stock
            db_obj.cantidad_minima = ing_obj.cantidad_minima
            db_obj.cantidad_reservada = ing_obj.cantidad_reservada
            db_obj.updated_at = datetime.utcnow()
            self._session.add(db_obj)
            self._session.flush()
            self._session.refresh(db_obj)
            return _to_domain(db_obj)

        db_obj = self._session.get(IngredienteDB, ingrediente_id)
        if not db_obj:
            return None

        if nombre is not None and nombre != db_obj.nombre:
            conflict = self._session.exec(
                select(IngredienteDB).where(IngredienteDB.nombre == nombre)
            ).first()
            if conflict:
                raise ValueError(f"Ingrediente '{nombre}' ya existe")
            db_obj.nombre = nombre

        if descripcion is not None:
            db_obj.descripcion = descripcion

        if cantidad_stock is not None:
            if cantidad_stock < 0:
                raise ValueError("cantidad_stock no puede ser negativa")
            db_obj.cantidad_stock = cantidad_stock

        if cantidad_minima is not None:
            if cantidad_minima < 0:
                raise ValueError("cantidad_minima no puede ser negativa")
            db_obj.cantidad_minima = cantidad_minima

        db_obj.updated_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_domain(db_obj)

    def soft_delete(self, ingrediente_id: int) -> bool:
        """Marcar ingrediente como inactivo (soft delete) — idempotente."""
        db_obj = self._session.get(IngredienteDB, ingrediente_id)
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

    def puede_descontar(self, ingrediente_id: int, cantidad: int) -> bool:
        """Verifica si hay stock suficiente."""
        ingrediente = self.find_by_id(ingrediente_id)
        if not ingrediente:
            raise ValueError(f"Ingrediente {ingrediente_id} no existe")
        if not ingrediente.is_active:
            raise ValueError(f"Ingrediente {ingrediente_id} no está activo")
        return ingrediente.puede_descontar(cantidad)

    def stock_disponible(self, ingrediente_id: int) -> int:
        """Obtener stock disponible de un ingrediente."""
        ingrediente = self.find_by_id(ingrediente_id)
        if not ingrediente:
            raise ValueError(f"Ingrediente {ingrediente_id} no existe")
        return ingrediente.stock_disponible

    def find_all(self, include_inactive: bool = False) -> List[Ingrediente]:
        """Obtener todos los ingredientes (activos o todos)."""
        stmt = select(IngredienteDB).order_by(IngredienteDB.id)
        if not include_inactive:
            stmt = stmt.where(IngredienteDB.is_active == True)  # noqa: E712
        db_objs = self._session.exec(stmt).all()
        return [_to_domain(obj) for obj in db_objs]
