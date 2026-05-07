"""
Script de migración para crear tabla usuarios en PostgreSQL.
Ejecutar: python config/migrations.py
"""

import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env', override=True)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_USER = os.getenv('DB_USER', '')
DB_PASS = os.getenv('DB_PASS', '')
DB_NAME = os.getenv('DB_NAME', '')

def get_connection():
    """Conectar a PostgreSQL"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

def create_usuarios_table():
    """Crear tabla usuarios si no existe"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Crear enum tipo role si no existe
        cursor.execute("""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'role_enum') THEN
                    CREATE TYPE role_enum AS ENUM ('admin', 'customer');
                END IF;
            END $$;
        """)
        
        # Crear tabla usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role role_enum NOT NULL DEFAULT 'customer',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT email_format CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
            );
        """)
        
        # Crear índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
            CREATE INDEX IF NOT EXISTS idx_usuarios_is_active ON usuarios(is_active);
        """)
        
        conn.commit()
        print("✅ Tabla usuarios creada exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al crear tabla: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def seed_admin_user():
    """Insertar usuario admin por defecto para testing (sin contraseña real, solo para desarrollo)"""
    from passlib.context import CryptContext
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si ya existe admin
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", ("admin@foodstore.local",))
        if cursor.fetchone():
            print("ℹ️  Usuario admin ya existe")
            return
        
        # Crear hash de contraseña (temporal)
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_pwd = pwd_context.hash("admin123")  # Cambiar en producción
        
        cursor.execute(
            "INSERT INTO usuarios (email, password_hash, role, is_active) VALUES (%s, %s, %s, %s)",
            ("admin@foodstore.local", hashed_pwd, "admin", True)
        )
        
        conn.commit()
        print("✅ Usuario admin creado: admin@foodstore.local (cambiar contraseña en producción)")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al insertar admin: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔧 Iniciando migración de usuarios...")
    create_usuarios_table()
    seed_admin_user()
    print("✅ Migración completada")
