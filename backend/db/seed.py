"""
Seed de datos iniciales para Food Store.

Carga el administrador por defecto y categorías, ingredientes y productos de ejemplo
en PostgreSQL usando PostgreSQLUnitOfWork.

Idempotente: verifica existencia por nombre antes de insertar cada registro.
Para productos ya existentes: actualiza stock si es 0 y agrega ingredientes faltantes.

Uso desde startup de FastAPI:
    from backend.db.seed import seed_initial_data
    seed_initial_data()

Uso desde línea de comandos:
    python -m backend.db.seed
"""

from datetime import datetime
from sqlmodel import Session, select

from backend.core.database import engine
from backend.core.uow_postgresql import PostgreSQLUnitOfWork
from backend.core.security import PasswordService
from backend.modules.auth.model import RoleEnum
from backend.modules.ingredientes.sqlmodel_model import IngredienteDB
from backend.modules.productos.sqlmodel_model import ProductoDB, ProductoCategoriaDB, ProductoIngredienteDB


def seed_initial_data() -> None:
    """Pre-carga datos iniciales en PostgreSQL."""
    with Session(engine) as session:
        uow = PostgreSQLUnitOfWork(session)
        _seed_admin(uow)
        _seed_categorias(uow)
        _seed_ingredientes(uow, session)
        _seed_productos(uow, session)


def _seed_admin(uow: PostgreSQLUnitOfWork) -> None:
    existing = uow.usuarios.find_by_email("admin@foodstore.com")
    if existing:
        return

    password_hash = PasswordService.hash_password("Admin1234!")
    uow.usuarios.create(
        email="admin@foodstore.com",
        password_hash=password_hash,
        role=RoleEnum.ADMIN,
    )
    uow.commit()


def _seed_categorias(uow: PostgreSQLUnitOfWork) -> None:
    categorias_data = [
        ("Pizzas", "Pizzas artesanales con ingredientes frescos"),
        ("Hamburguesas", "Hamburguesas gourmet"),
        ("Bebidas", "Gaseosas, jugos y agua"),
        ("Postres", "Postres y dulces del día"),
        ("Ensaladas", "Ensaladas frescas y nutritivas"),
    ]

    created_any = False
    for nombre, descripcion in categorias_data:
        existing = uow.categorias.find_by_name(nombre)
        if existing:
            continue
        uow.categorias.create(nombre=nombre, descripcion=descripcion)
        created_any = True

    if created_any:
        uow.commit()


def _seed_ingredientes(uow: PostgreSQLUnitOfWork, session: Session) -> None:
    """Seed de ingredientes con stock realista."""
    ingredientes_data = [
        # (nombre, es_alergeno, unidad_medida, cantidad_stock, cantidad_minima)
        ("Harina",          True,  "gramos",   5000, 500),
        ("Gluten",          True,  "gramos",   5000, 500),
        ("Lactosa",         True,  "gramos",   5000, 500),
        ("Maní",            True,  "gramos",   2000, 200),
        ("Tomate",          False, "gramos",   4000, 400),
        ("Queso",           False, "gramos",   3000, 300),
        ("Lechuga",         False, "gramos",   2000, 200),
        ("Cebolla",         False, "gramos",   2000, 200),
        ("Jamón",           False, "gramos",   2000, 200),
        ("Carne Molida",    False, "gramos",   3000, 300),
        ("Salsa de Tomate", False, "mililitros",2000, 200),
        ("Pepperoni",       False, "gramos",   1500, 150),
        ("Azúcar",          False, "gramos",   3000, 300),
        ("Manteca",         True,  "gramos",   1500, 150),
        ("Cacao",           False, "gramos",   1000, 100),
    ]

    created_any = False
    now = datetime.utcnow()

    for nombre, es_alergeno, unidad_medida, cantidad_stock, cantidad_minima in ingredientes_data:
        existing = session.exec(
            select(IngredienteDB).where(IngredienteDB.nombre == nombre)
        ).first()
        if existing:
            # Actualizar stock si está en 0
            if existing.cantidad_stock == 0:
                existing.cantidad_stock = cantidad_stock
                existing.cantidad_minima = cantidad_minima
                session.add(existing)
                created_any = True
            continue

        db_obj = IngredienteDB(
            nombre=nombre,
            descripcion="",
            unidad_medida=unidad_medida,
            cantidad_stock=cantidad_stock,
            cantidad_minima=cantidad_minima,
            cantidad_reservada=0,
            es_alergeno=es_alergeno,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        session.add(db_obj)
        created_any = True

    if created_any:
        session.flush()
        uow.commit()


def _seed_productos(uow: PostgreSQLUnitOfWork, session: Session) -> None:
    """Seed de productos con categorías e ingredientes asociados."""

    categorias = uow.categorias.find_all()
    cat_map = {c.nombre: c.id for c in categorias}

    ingredientes_db = session.exec(select(IngredienteDB)).all()
    ing_map = {i.nombre: i.id for i in ingredientes_db}

    # (nombre, descripcion, precio, stock, categoria, [(ingrediente, quantity_required)])
    productos_data = [
        (
            "Pizza Margherita",
            "Salsa de tomate, mozzarella y albahaca",
            1500.00, 20, "Pizzas",
            [("Harina", 200.0), ("Salsa de Tomate", 100.0), ("Queso", 150.0), ("Gluten", 10.0)],
        ),
        (
            "Pizza Pepperoni",
            "Salsa de tomate, mozzarella y pepperoni",
            1700.00, 15, "Pizzas",
            [("Harina", 200.0), ("Salsa de Tomate", 100.0), ("Queso", 130.0), ("Pepperoni", 80.0), ("Gluten", 10.0)],
        ),
        (
            "Hamburguesa Clásica",
            "Carne, lechuga, tomate, cebolla y queso",
            1200.00, 20, "Hamburguesas",
            [("Carne Molida", 200.0), ("Tomate", 50.0), ("Lechuga", 30.0), ("Cebolla", 30.0), ("Queso", 40.0)],
        ),
        (
            "Hamburguesa Doble",
            "Doble medallón de carne, jamón y queso derretido",
            1600.00, 15, "Hamburguesas",
            [("Carne Molida", 400.0), ("Jamón", 60.0), ("Queso", 60.0), ("Lechuga", 30.0), ("Tomate", 40.0)],
        ),
        (
            "Coca-Cola 500ml",
            "Bebida refrescante",
            400.00, 50, "Bebidas",
            [],
        ),
        (
            "Agua Mineral 500ml",
            "Agua mineral sin gas",
            200.00, 60, "Bebidas",
            [],
        ),
        (
            "Brownie de Chocolate",
            "Brownie casero con nueces y cacao",
            600.00, 30, "Postres",
            [("Harina", 150.0), ("Azúcar", 100.0), ("Manteca", 80.0), ("Cacao", 50.0), ("Maní", 30.0)],
        ),
        (
            "Ensalada Caesar",
            "Lechuga romana, aderezo caesar y crutones",
            900.00, 10, "Ensaladas",
            [("Lechuga", 150.0), ("Queso", 30.0)],
        ),
        (
            "Ensalada Mixta",
            "Lechuga, tomate, cebolla y jamón",
            800.00, 10, "Ensaladas",
            [("Lechuga", 120.0), ("Tomate", 80.0), ("Cebolla", 30.0), ("Jamón", 50.0)],
        ),
    ]

    now = datetime.utcnow()
    created_any = False

    for nombre, descripcion, precio, stock, categoria_nombre, ingredientes in productos_data:
        existing = session.exec(
            select(ProductoDB).where(ProductoDB.nombre == nombre)
        ).first()

        if existing:
            # Actualizar stock si es 0
            if existing.stock == 0:
                existing.stock = stock
                session.add(existing)
                created_any = True

            # Agregar ingredientes faltantes
            for ing_nombre, qty in ingredientes:
                ing_id = ing_map.get(ing_nombre)
                if ing_id is None:
                    continue
                rel_exists = session.exec(
                    select(ProductoIngredienteDB).where(
                        ProductoIngredienteDB.product_id == existing.id,
                        ProductoIngredienteDB.ingredient_id == ing_id,
                    )
                ).first()
                if not rel_exists:
                    session.add(ProductoIngredienteDB(
                        product_id=existing.id,
                        ingredient_id=ing_id,
                        quantity_required=qty,
                        created_at=now,
                        updated_at=now,
                    ))
                    created_any = True
            continue

        # Crear nuevo producto
        db_producto = ProductoDB(
            nombre=nombre,
            descripcion=descripcion,
            base_price=precio,
            status="active",
            stock=stock,
            created_at=now,
            updated_at=now,
        )
        session.add(db_producto)
        session.flush()
        session.refresh(db_producto)

        cat_id = cat_map.get(categoria_nombre)
        if cat_id is not None:
            session.add(ProductoCategoriaDB(
                producto_id=db_producto.id,
                categoria_id=cat_id,
            ))

        for ing_nombre, qty in ingredientes:
            ing_id = ing_map.get(ing_nombre)
            if ing_id is not None:
                session.add(ProductoIngredienteDB(
                    product_id=db_producto.id,
                    ingredient_id=ing_id,
                    quantity_required=qty,
                    created_at=now,
                    updated_at=now,
                ))

        created_any = True

    if created_any:
        session.flush()
        uow.commit()


if __name__ == "__main__":
    print("Seeding initial data...")
    seed_initial_data()
    print("Done.")
    print("  Admin user: admin@foodstore.com / Admin1234!")
    with Session(engine) as session:
        uow = PostgreSQLUnitOfWork(session)
        print(f"  Categorias:   {len(uow.categorias.find_all())}")
        print(f"  Ingredientes: {len(uow.ingredientes.find_all())}")
        print(f"  Productos:    {len(uow.productos.find_all())}")
