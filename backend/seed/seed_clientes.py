"""
Seed script para pre-cargar clientes de prueba en la BD.

Uso:
    python -m backend.seed.seed_clientes

Este script crea varios clientes con datos variados para testing.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime
from models.cliente import Cliente
from uow.inmemory import InMemoryUnitOfWork
from services.cliente_service import ClienteService


def seed_clientes():
    """Cargar clientes de prueba en la BD."""
    
    # Crear UoW e instanciar servicio
    uow = InMemoryUnitOfWork()
    service = ClienteService(uow)
    
    # Datos de prueba
    clientes_data = [
        {
            "nombre": "Juan Pérez",
            "email": "juan.perez@example.com",
            "telefono": "+54 11 1234 5678",
            "direccion": "Av. Corrientes 123, Buenos Aires, Argentina",
        },
        {
            "nombre": "María García López",
            "email": "maria.garcia@example.com",
            "telefono": "+54 11 2345 6789",
            "direccion": "Calle Lavalle 456, Apt 3B, Buenos Aires, Argentina",
        },
        {
            "nombre": "Carlos Rodríguez",
            "email": "carlos.rodriguez@example.com",
            "telefono": "+54 11 3456 7890",
            "direccion": "Paseo Colón 789, Piso 10, Buenos Aires, Argentina",
        },
        {
            "nombre": "Ana Martínez",
            "email": "ana.martinez@example.com",
            "telefono": "+54 11 4567 8901",
            "direccion": "Calle 9 de Julio 1000, Apt 1A, Buenos Aires, Argentina",
        },
        {
            "nombre": "Jorge López Villarreal",
            "email": "jorge.lopez@example.com",
            "telefono": "+54 11 5678 9012",
            "direccion": "Avenida Santa Fe 2000, Buenos Aires, Argentina",
        },
        {
            "nombre": "Sofia Chen",
            "email": "sofia.chen@example.com",
            "telefono": "+54 11 6789 0123",
            "direccion": "Calle Florida 500, San Isidro, Buenos Aires, Argentina",
        },
        {
            "nombre": "Pablo González",
            "email": "pablo.gonzalez@example.com",
            "telefono": "+54 11 7890 1234",
            "direccion": "Paseo Rivadavia 300, Recoleta, Buenos Aires, Argentina",
        },
        {
            "nombre": "Isabel Fernández",
            "email": "isabel.fernandez@example.com",
            "telefono": "+54 11 8901 2345",
            "direccion": "Calle Hipólito Yrigoyen 800, Belgrano, Buenos Aires, Argentina",
        },
    ]
    
    # Crear clientes
    created_count = 0
    for idx, cliente_data in enumerate(clientes_data, start=1):
        try:
            result = service.create_cliente(
                nombre=cliente_data["nombre"],
                email=cliente_data["email"],
                telefono=cliente_data["telefono"],
                direccion=cliente_data["direccion"],
                requesting_user_role="ADMIN"
            )
            print(f"✓ Cliente #{idx}: {result['nombre']} ({result['email']})")
            created_count += 1
        except Exception as e:
            print(f"✗ Error creando cliente #{idx}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Total de clientes creados: {created_count}/{len(clientes_data)}")
    print(f"{'='*60}")
    
    return created_count == len(clientes_data)


def seed_clientes_with_fixtures():
    """
    Cargar clientes de prueba con roles variados para testing RBAC.
    
    Fixtures:
    - ADMIN: acceso completo
    - USER (clientes normales): acceso limitado a su perfil
    """
    
    uow = InMemoryUnitOfWork()
    service = ClienteService(uow)
    
    # Admin user fixture (para usar en tests con ADMIN role)
    admin_fixture = {
        "nombre": "Admin User",
        "email": "admin@foodstore.local",
        "telefono": "+54 11 0000 0000",
        "direccion": "Admin Office, Buenos Aires, Argentina",
    }
    
    # Regular user fixtures
    user_fixtures = [
        {
            "nombre": "Test User 1",
            "email": "testuser1@foodstore.local",
            "telefono": "+54 11 1111 1111",
            "direccion": "Test Address 1, Buenos Aires, Argentina",
        },
        {
            "nombre": "Test User 2",
            "email": "testuser2@foodstore.local",
            "telefono": "+54 11 2222 2222",
            "direccion": "Test Address 2, Buenos Aires, Argentina",
        },
        {
            "nombre": "Test User 3",
            "email": "testuser3@foodstore.local",
            "telefono": "+54 11 3333 3333",
            "direccion": "Test Address 3, Buenos Aires, Argentina",
        },
    ]
    
    fixtures = {"admin": admin_fixture, "users": user_fixtures}
    
    # Crear admin
    try:
        admin_result = service.create_cliente(
            nombre=admin_fixture["nombre"],
            email=admin_fixture["email"],
            telefono=admin_fixture["telefono"],
            direccion=admin_fixture["direccion"],
            requesting_user_role="ADMIN"
        )
        print(f"✓ Admin fixture: {admin_result['nombre']}")
    except Exception as e:
        print(f"✗ Error creating admin fixture: {e}")
        return False
    
    # Crear users
    for idx, user_data in enumerate(user_fixtures, start=1):
        try:
            user_result = service.create_cliente(
                nombre=user_data["nombre"],
                email=user_data["email"],
                telefono=user_data["telefono"],
                direccion=user_data["direccion"],
                requesting_user_role="ADMIN"  # Creados por admin
            )
            print(f"✓ User fixture #{idx}: {user_result['nombre']}")
        except Exception as e:
            print(f"✗ Error creating user fixture #{idx}: {e}")
            return False
    
    return True


if __name__ == "__main__":
    print("Seeding clientes...")
    success = seed_clientes()
    
    print("\nSeeding fixtures para RBAC tests...")
    fixtures_success = seed_clientes_with_fixtures()
    
    if success and fixtures_success:
        print("\n✅ Seed completado exitosamente!")
        sys.exit(0)
    else:
        print("\n❌ Seed falló parcialmente")
        sys.exit(1)
