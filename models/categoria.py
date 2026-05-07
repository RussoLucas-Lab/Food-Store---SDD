from datetime import datetime
from typing import Optional

class Categoria:
    """
    Modelo de Categoría para el catálogo de productos.
    
    Atributos:
        id: Identificador único (PK)
        nombre: Nombre de la categoría (unique)
        descripcion: Descripción opcional
        is_active: Estado de la categoría (activo/inactivo)
        created_at: Timestamp de creación
        updated_at: Timestamp de última actualización
        deleted_at: Timestamp de soft delete (None si activa)
    """
    
    def __init__(
        self,
        id: int,
        nombre: str,
        descripcion: str = "",
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None
    ):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
    
    def __repr__(self) -> str:
        return f"<Categoria id={self.id} nombre='{self.nombre}' is_active={self.is_active}>"
    
    def to_dict(self) -> dict:
        """Serializa Categoría a diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "deleted_at": self.deleted_at.isoformat() if isinstance(self.deleted_at, datetime) else self.deleted_at,
        }
