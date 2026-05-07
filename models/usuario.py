from enum import Enum
from datetime import datetime
from typing import Optional

class RoleEnum(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"

class Usuario:
    def __init__(
        self,
        id: int,
        email: str,
        password_hash: str,
        role: RoleEnum = RoleEnum.CUSTOMER,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        nombre: Optional[str] = None  # Compatibilidad con cambio anterior
    ):
        self.id = id
        self.nombre = nombre or email.split("@")[0]  # Por defecto, usar parte del email
        self.email = email
        self.password_hash = password_hash
        self.role = role if isinstance(role, RoleEnum) else RoleEnum(role)
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self):
        return f"<Usuario id={self.id} email={self.email} role={self.role.value} is_active={self.is_active}>"

    def to_dict(self, include_password_hash: bool = False):
        """Serializa Usuario a diccionario, excluyendo password_hash por defecto"""
        data = {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }
        if include_password_hash:
            data["password_hash"] = self.password_hash
        return data
