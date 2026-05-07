"""
Modelos de dominio para Food Store.

Contiene las entidades principales: Usuario, Categoría, Ingrediente, Producto, Cliente.
"""

from models.usuario import Usuario, RoleEnum
from models.categoria import Categoria

__all__ = [
    "Usuario",
    "RoleEnum",
    "Categoria",
]
