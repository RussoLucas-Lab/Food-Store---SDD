from datetime import datetime
from typing import Optional


class Cliente:
    """
    Modelo de Cliente para el sistema Food Store.

    Atributos:
        id: Identificador único (PK)
        nombre: Nombre del cliente (requerido)
        email: Email del cliente (unique, requerido)
        telefono: Teléfono de contacto (opcional)
        direccion: Dirección de entrega (requerido)
        activo: Estado del cliente (activo/inactivo, soft delete)
        user_id: FK a Usuario (opcional, para autenticación integrada)
        created_at: Timestamp de creación
        updated_at: Timestamp de última actualización
    """

    def __init__(
        self,
        id: int,
        nombre: str,
        email: str,
        direccion: str,
        telefono: Optional[str] = None,
        activo: bool = True,
        user_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        self.activo = activo
        self.user_id = user_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Cliente id={self.id} nombre='{self.nombre}' email='{self.email}' activo={self.activo}>"

    def to_dict(self) -> dict:
        """Serializa Cliente a diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "activo": self.activo,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }
