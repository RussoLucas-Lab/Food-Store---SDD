"""
Implementación PostgreSQL de IUsuarioRepository usando SQLModel Session.

Trabaja con la tabla `usuarios` via UsuarioDB (SQLModel) y devuelve
objetos de dominio Usuario (model.py) para mantener compatibilidad
con los services existentes.
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from .repository import IUsuarioRepository
from .model import Usuario, RoleEnum
from .sqlmodel_model import UsuarioDB


def _to_domain(db_obj: UsuarioDB) -> Usuario:
    """Convertir UsuarioDB (SQLModel) → Usuario (dominio)."""
    return Usuario(
        id=db_obj.id,
        email=db_obj.email,
        password_hash=db_obj.password_hash,
        nombre=db_obj.nombre,
        role=RoleEnum(db_obj.role),
        is_active=db_obj.is_active,
        created_at=db_obj.created_at,
        updated_at=db_obj.updated_at,
    )


class PostgreSQLUsuarioRepository(IUsuarioRepository):
    """Implementación PostgreSQL de IUsuarioRepository."""

    def __init__(self, session: Session):
        self._session = session

    def create(self, email: str, password_hash: str, role: RoleEnum = RoleEnum.CUSTOMER, nombre: Optional[str] = None) -> Usuario:
        """Crear nuevo usuario."""
        # Verificar unicidad de email
        existing = self._session.exec(
            select(UsuarioDB).where(UsuarioDB.email == email)
        ).first()
        if existing:
            raise ValueError(f"Email {email} ya registrado")

        now = datetime.utcnow()
        db_obj = UsuarioDB(
            email=email,
            password_hash=password_hash,
            nombre=nombre or email.split("@")[0],
            role=role.value if isinstance(role, RoleEnum) else role,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self._session.add(db_obj)
        self._session.flush()  # obtener id sin commit
        self._session.refresh(db_obj)
        return _to_domain(db_obj)

    def find_by_email(self, email: str) -> Optional[Usuario]:
        """Buscar usuario por email."""
        db_obj = self._session.exec(
            select(UsuarioDB).where(UsuarioDB.email == email)
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def find_by_id(self, user_id: int) -> Optional[Usuario]:
        """Buscar usuario por id."""
        db_obj = self._session.get(UsuarioDB, user_id)
        return _to_domain(db_obj) if db_obj else None

    def update(self, user_id: int, **kwargs) -> Optional[Usuario]:
        """Actualizar usuario."""
        db_obj = self._session.get(UsuarioDB, user_id)
        if not db_obj:
            return None

        allowed = {"email", "password_hash", "nombre", "role", "is_active"}
        for key, value in kwargs.items():
            if key in allowed:
                # Normalizar role a string si es RoleEnum
                if key == "role" and isinstance(value, RoleEnum):
                    value = value.value
                setattr(db_obj, key, value)

        db_obj.updated_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_domain(db_obj)

    def deactivate(self, user_id: int) -> bool:
        """Desactivar usuario."""
        db_obj = self._session.get(UsuarioDB, user_id)
        if not db_obj:
            return False
        db_obj.is_active = False
        db_obj.updated_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        return True

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Usuario]:
        """Listar todos los usuarios con paginación."""
        statement = select(UsuarioDB).offset(offset).limit(limit)
        db_objs = self._session.exec(statement).all()
        return [_to_domain(obj) for obj in db_objs]
