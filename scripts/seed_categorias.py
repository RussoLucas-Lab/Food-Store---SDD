"""
Seed script para categorías iniciales de Food Store.

Este script crea ~10 categorías típicas para el catálogo de productos.
Úsalo después de crear la tabla 'categorias' en la BD.

Uso:
    python scripts/seed_categorias.py
"""

from datetime import datetime
from models.categoria import Categoria

# Categorías iniciales
INITIAL_CATEGORIES = [
    {
        "nombre": "Bebidas Frías",
        "descripcion": "Bebidas refrescantes: jugos, gaseosas, cervezas frías"
    },
    {
        "nombre": "Bebidas Calientes",
        "descripcion": "Café, té, chocolate caliente y otras bebidas calientes"
    },
    {
        "nombre": "Postres",
        "descripcion": "Postres, tortas, tartas, helados y dulces"
    },
    {
        "nombre": "Hamburguesas",
        "descripcion": "Hamburguesas, sándwiches y comidas rápidas"
    },
    {
        "nombre": "Ensaladas",
        "descripcion": "Ensaladas frescas y opciones vegetarianas"
    },
    {
        "nombre": "Platos Principales",
        "descripcion": "Comidas completas, milanesas, carnes y pasta"
    },
    {
        "nombre": "Vegetarianos",
        "descripcion": "Opciones vegetarianas y veganas"
    },
    {
        "nombre": "Extras",
        "descripcion": "Acompañamientos: papas fritas, aderezos, salsas"
    },
    {
        "nombre": "Desayunos",
        "descripcion": "Opciones de desayuno: medialunas, tostadas, huevos"
    },
    {
        "nombre": "Bebidas Alcohólicas",
        "descripcion": "Cervezas, vinos, licores y bebidas alcohólicas"
    },
]


def seed_categories(uow):
    """
    Siembra las categorías iniciales en la BD.
    
    Args:
        uow: Instancia de Unit of Work
    
    Returns:
        list[Categoria]: Lista de categorías creadas
    """
    created = []
    
    for idx, cat_data in enumerate(INITIAL_CATEGORIES, start=1):
        try:
            categoria = uow.categorias.create(
                nombre=cat_data["nombre"],
                descripcion=cat_data["descripcion"]
            )
            created.append(categoria)
            print(f"✓ Categoría {idx}: {categoria.nombre}")
        except ValueError as e:
            print(f"✗ Error al crear categoría {idx}: {e}")
    
    uow.commit()
    print(f"\n{len(created)}/{len(INITIAL_CATEGORIES)} categorías creadas exitosamente.")
    return created


if __name__ == "__main__":
    # Ejemplo de uso (si se ejecuta directamente)
    from uow.inmemory import InMemoryUnitOfWork
    
    uow = InMemoryUnitOfWork()
    seed_categories(uow)
