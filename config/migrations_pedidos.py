"""
Script de migración para crear tablas de pedidos en PostgreSQL.
Crear:
  1. estado_pedido (enum/tabla)
  2. pedidos
  3. detalles_pedido
  4. historial_estado_pedido (append-only)

Ejecutar: python config/migrations_pedidos.py
"""

import os
import psycopg2
import json
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

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

def create_estado_pedido_enum():
    """Crear enum de estados de pedido"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Crear enum tipo estado_pedido si no existe
        cursor.execute("""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_pedido_enum') THEN
                    CREATE TYPE estado_pedido_enum AS ENUM ('PENDIENTE', 'CONFIRMADO', 'EN_PREPARACION', 'LISTO', 'EN_VIAJE', 'ENTREGADO', 'CANCELADO');
                END IF;
            END $$;
        """)
        
        conn.commit()
        print("[OK] Enum estado_pedido_enum creado exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al crear enum: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def create_pedidos_table():
    """Crear tabla pedidos"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id SERIAL PRIMARY KEY,
                cliente_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                estado estado_pedido_enum NOT NULL DEFAULT 'PENDIENTE',
                direccion_snapshot TEXT NOT NULL,
                total NUMERIC(10, 2) NOT NULL CHECK (total > 0),
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Crear índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pedidos_cliente_id ON pedidos(cliente_id);
            CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado);
            CREATE INDEX IF NOT EXISTS idx_pedidos_creado_en ON pedidos(creado_en DESC);
        """)
        
        conn.commit()
        print("[OK] Tabla pedidos creada exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al crear tabla pedidos: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def create_detalles_pedido_table():
    """Crear tabla detalles_pedido"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalles_pedido (
                id SERIAL PRIMARY KEY,
                pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
                producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
                cantidad INTEGER NOT NULL CHECK (cantidad > 0),
                precio_snapshot NUMERIC(10, 2) NOT NULL CHECK (precio_snapshot >= 0),
                personalizacion INTEGER[] DEFAULT '{}',
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Crear índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_detalles_pedido_pedido_id ON detalles_pedido(pedido_id);
            CREATE INDEX IF NOT EXISTS idx_detalles_pedido_producto_id ON detalles_pedido(producto_id);
        """)
        
        conn.commit()
        print("[OK] Tabla detalles_pedido creada exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al crear tabla detalles_pedido: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def create_historial_estado_pedido_table():
    """Crear tabla historial_estado_pedido (append-only)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_estado_pedido (
                id SERIAL PRIMARY KEY,
                pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
                estado_anterior estado_pedido_enum,
                estado_nuevo estado_pedido_enum NOT NULL,
                usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                observacion TEXT
            );
        """)
        
        # Crear índices (append-only, sin actualizaciones)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_historial_pedido_id ON historial_estado_pedido(pedido_id);
            CREATE INDEX IF NOT EXISTS idx_historial_timestamp ON historial_estado_pedido(timestamp DESC);
        """)
        
        conn.commit()
        print("[OK] Tabla historial_estado_pedido creada exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al crear tabla historial_estado_pedido: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def verify_tables():
    """Verificar que las tablas fueron creadas correctamente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar que las tablas existen
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('pedidos', 'detalles_pedido', 'historial_estado_pedido')
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("\n[OK] Tablas creadas:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Mostrar columnas de cada tabla
        for table_name in ['pedidos', 'detalles_pedido', 'historial_estado_pedido']:
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            
            print(f"\n[INFO] Columnas de {table_name}:")
            for col in cursor.fetchall():
                nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                print(f"   - {col[0]}: {col[1]} ({nullable})")
        
    except Exception as e:
        print(f"[ERROR] Error al verificar tablas: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    """Ejecutar todas las migraciones"""
    print("[INFO] Iniciando migracion de tablas de pedidos...\n")
    
    try:
        create_estado_pedido_enum()
        create_pedidos_table()
        create_detalles_pedido_table()
        create_historial_estado_pedido_table()
        verify_tables()
        
        print("\n[OK] Migracion completada exitosamente!")
        
    except Exception as e:
        print(f"\n[ERROR] Error durante la migracion: {e}")
        raise

if __name__ == '__main__':
    main()
