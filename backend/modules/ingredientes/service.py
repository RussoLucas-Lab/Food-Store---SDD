"""
Service para operaciones de negocio de Ingredientes.
"""

from typing import Optional, List, Dict
from backend.core.uow import IUnitOfWork

# Unidades de medida válidas
VALID_UNITS = {"gramos", "litros", "unidades", "kilos", "mililitros"}


class IngredientService:
    """
    Servicio de lógica de negocio para Ingredientes.
    """

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def create_ingrediente(
        self,
        nombre: str,
        unidad_medida: str,
        cantidad_stock: float,
        cantidad_minima: float,
        descripcion: str = "",
        categoria_id: Optional[int] = None
    ) -> Dict:
        """Crear nuevo ingrediente con validaciones."""
        if not nombre or not nombre.strip():
            raise ValueError("Nombre requerido")

        nombre = nombre.strip()

        if len(nombre) > 100:
            raise ValueError("Nombre no puede exceder 100 caracteres")

        if not unidad_medida or unidad_medida.lower() not in VALID_UNITS:
            raise ValueError(f"Unidad medida debe ser: {', '.join(VALID_UNITS)}")

        if cantidad_stock < 0:
            raise ValueError("Stock no puede ser negativo")

        if cantidad_minima < 0:
            raise ValueError("Cantidad mínima no puede ser negativa")

        if descripcion and len(descripcion) > 500:
            raise ValueError("Descripción no puede exceder 500 caracteres")

        existing = self.uow.ingredientes.find_by_name(nombre)
        if existing:
            raise ValueError(f"Ingrediente '{nombre}' ya existe")

        ingrediente = self.uow.ingredientes.create(
            nombre=nombre,
            unidad_medida=unidad_medida.lower(),
            cantidad_stock=cantidad_stock,
            cantidad_minima=cantidad_minima,
            descripcion=descripcion or "",
            categoria_id=categoria_id
        )
        self.uow.commit()

        return ingrediente.to_dict()

    def update_ingrediente(
        self,
        id: int,
        nombre: Optional[str] = None,
        unidad_medida: Optional[str] = None,
        cantidad_stock: Optional[float] = None,
        cantidad_minima: Optional[float] = None,
        descripcion: Optional[str] = None,
        categoria_id: Optional[int] = None
    ) -> Dict:
        """Actualizar ingrediente existente."""
        ingrediente = self.uow.ingredientes.find_by_id(id)
        if not ingrediente:
            raise ValueError(f"Ingrediente {id} no existe")

        if nombre is not None:
            nombre = nombre.strip()
            if not nombre:
                raise ValueError("Nombre requerido")
            if len(nombre) > 100:
                raise ValueError("Nombre no puede exceder 100 caracteres")

            existing = self.uow.ingredientes.find_by_name(nombre)
            if existing and existing.id != id:
                raise ValueError(f"Nombre ya está en uso")

            ingrediente.nombre = nombre

        if unidad_medida is not None:
            if unidad_medida.lower() not in VALID_UNITS:
                raise ValueError(f"Unidad medida debe ser: {', '.join(VALID_UNITS)}")
            ingrediente.unidad_medida = unidad_medida.lower()

        if cantidad_stock is not None:
            if cantidad_stock < 0:
                raise ValueError("Stock no puede ser negativo")
            ingrediente.cantidad_stock = cantidad_stock

        if cantidad_minima is not None:
            if cantidad_minima < 0:
                raise ValueError("Cantidad mínima no puede ser negativa")
            ingrediente.cantidad_minima = cantidad_minima

        if descripcion is not None:
            if len(descripcion) > 500:
                raise ValueError("Descripción no puede exceder 500 caracteres")
            ingrediente.descripcion = descripcion

        if categoria_id is not None:
            ingrediente.categoria_id = categoria_id

        self.uow.ingredientes.update(ingrediente)
        self.uow.commit()

        return ingrediente.to_dict()

    def delete_ingrediente(self, id: int) -> Dict:
        """Soft-delete de ingrediente."""
        ingrediente = self.uow.ingredientes.find_by_id(id)
        if not ingrediente:
            raise ValueError(f"Ingrediente {id} no existe")

        products_using = self.uow.productos.count_by_ingredient(id)
        if products_using > 0:
            raise ValueError(f"Ingrediente '{ingrediente.nombre}' está en uso por {products_using} productos activos")

        self.uow.ingredientes.soft_delete(id)
        self.uow.commit()

        return ingrediente.to_dict()

    def get_ingrediente(self, id: int) -> Dict:
        """Obtener ingrediente por ID."""
        ingrediente = self.uow.ingredientes.find_by_id(id)
        if not ingrediente:
            raise ValueError(f"Ingrediente {id} no existe")

        return ingrediente.to_dict()

    def list_ingredientes(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        unidad_medida: Optional[str] = None,
        categoria_id: Optional[int] = None
    ) -> List[Dict]:
        """Listar ingredientes con paginación y filtros opcionales."""
        ingredientes = self.uow.ingredientes.list_active(
            skip=skip,
            limit=limit,
            unidad_medida=unidad_medida,
            categoria_id=categoria_id
        )

        return [ing.to_dict() for ing in ingredientes]

    def get_stock_history(self, id: int) -> List[Dict]:
        """Obtener historial de cambios de stock para un ingrediente."""
        ingrediente = self.uow.ingredientes.find_by_id(id)
        if not ingrediente:
            raise ValueError(f"Ingrediente {id} no existe")

        history = self.uow.ingredientes.get_stock_history(id)
        return history if history else []
