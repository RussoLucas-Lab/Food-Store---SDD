"""
Implementación PostgreSQL de IDireccionRepository usando SQLModel Session.
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from .repository import IDireccionRepository
from .model import DireccionEntrega
from .sqlmodel_model import DireccionEntregaDB


def _to_domain(db_obj: DireccionEntregaDB) -> DireccionEntrega:
    """Convertir DireccionEntregaDB → DireccionEntrega (dominio)."""
    return DireccionEntrega(
        id=db_obj.id,
        cliente_id=db_obj.cliente_id,
        calle=db_obj.calle,
        numero=db_obj.numero,
        ciudad=db_obj.ciudad,
        provincia=db_obj.provincia,
        codigo_postal=db_obj.codigo_postal,
        piso=db_obj.piso,
        departamento=db_obj.departamento,
        referencia=db_obj.referencia,
        es_predeterminada=db_obj.es_predeterminada,
        activo=db_obj.activo,
        created_at=db_obj.created_at,
        updated_at=db_obj.updated_at,
    )


class PostgreSQLDireccionRepository(IDireccionRepository):
    """Implementación PostgreSQL de IDireccionRepository."""

    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        cliente_id: int,
        calle: str,
        numero: str,
        ciudad: str,
        provincia: str,
        codigo_postal: str,
        piso: Optional[str] = None,
        departamento: Optional[str] = None,
        referencia: Optional[str] = None,
        es_predeterminada: bool = False,
    ) -> DireccionEntrega:
        """Crear nueva dirección."""
        now = datetime.utcnow()
        db_obj = DireccionEntregaDB(
            cliente_id=cliente_id,
            calle=calle,
            numero=numero,
            ciudad=ciudad,
            provincia=provincia,
            codigo_postal=codigo_postal,
            piso=piso,
            departamento=departamento,
            referencia=referencia,
            es_predeterminada=es_predeterminada,
            activo=True,
            created_at=now,
            updated_at=now,
        )
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_domain(db_obj)

    def get_by_id(self, direccion_id: int) -> Optional[DireccionEntrega]:
        """Buscar dirección por id (solo activas)."""
        db_obj = self._session.exec(
            select(DireccionEntregaDB).where(
                DireccionEntregaDB.id == direccion_id,
                DireccionEntregaDB.activo == True,  # noqa: E712
            )
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def list_by_cliente(self, cliente_id: int) -> List[DireccionEntrega]:
        """Listar direcciones activas de un cliente."""
        db_objs = self._session.exec(
            select(DireccionEntregaDB)
            .where(
                DireccionEntregaDB.cliente_id == cliente_id,
                DireccionEntregaDB.activo == True,  # noqa: E712
            )
            .order_by(DireccionEntregaDB.id)
        ).all()
        return [_to_domain(obj) for obj in db_objs]

    def update(self, direccion_id: int, **campos) -> Optional[DireccionEntrega]:
        """Actualizar campos de una dirección existente."""
        db_obj = self._session.get(DireccionEntregaDB, direccion_id)
        if not db_obj:
            return None

        allowed_fields = {
            "calle", "numero", "ciudad", "provincia", "codigo_postal",
            "piso", "departamento", "referencia", "es_predeterminada",
        }
        for key, value in campos.items():
            if key in allowed_fields:
                setattr(db_obj, key, value)

        db_obj.updated_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_domain(db_obj)

    def soft_delete(self, direccion_id: int) -> bool:
        """Marcar dirección como inactiva (soft delete)."""
        db_obj = self._session.get(DireccionEntregaDB, direccion_id)
        if not db_obj:
            return False
        db_obj.activo = False
        db_obj.updated_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        return True

    def count_by_cliente(self, cliente_id: int) -> int:
        """Contar direcciones activas de un cliente."""
        db_objs = self._session.exec(
            select(DireccionEntregaDB).where(
                DireccionEntregaDB.cliente_id == cliente_id,
                DireccionEntregaDB.activo == True,  # noqa: E712
            )
        ).all()
        return len(db_objs)

    def set_predeterminada(self, direccion_id: int) -> Optional[DireccionEntrega]:
        """Marcar una dirección como predeterminada, desmarcar el resto del cliente."""
        target = self._session.exec(
            select(DireccionEntregaDB).where(
                DireccionEntregaDB.id == direccion_id,
                DireccionEntregaDB.activo == True,  # noqa: E712
            )
        ).first()
        if not target:
            return None

        # Desmarcar todas las del mismo cliente
        otras = self._session.exec(
            select(DireccionEntregaDB).where(
                DireccionEntregaDB.cliente_id == target.cliente_id,
                DireccionEntregaDB.id != direccion_id,
                DireccionEntregaDB.activo == True,  # noqa: E712
            )
        ).all()
        now = datetime.utcnow()
        for otra in otras:
            otra.es_predeterminada = False
            otra.updated_at = now
            self._session.add(otra)

        target.es_predeterminada = True
        target.updated_at = now
        self._session.add(target)
        self._session.flush()
        self._session.refresh(target)
        return _to_domain(target)
