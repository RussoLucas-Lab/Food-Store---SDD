"""
Script de migración para crear tablas de productos.
Ejecutar: python config/migrations_productos.py
"""

import os
import psycopg2
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

def run_migration_file(cursor, sql_file):
    """Ejecutar un archivo SQL de migración"""
    with open(sql_file, 'r') as f:
        sql = f.read()
        cursor.execute(sql)

def create_productos_tables():
    """Crear tablas de productos: productos, product_categories, product_ingredients"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        migrations_dir = Path(__file__).parent.parent / 'docs' / 'migrations'
        
        # Ejecutar migraciones en orden
        migration_files = [
            migrations_dir / '002_create_productos.sql',
            migrations_dir / '003_create_product_categories.sql',
            migrations_dir / '004_create_product_ingredients.sql',
        ]
        
        for migration_file in migration_files:
            if migration_file.exists():
                print(f"Ejecutando {migration_file.name}...")
                run_migration_file(cursor, migration_file)
                conn.commit()
                print(f"✅ {migration_file.name} ejecutada exitosamente")
            else:
                print(f"⚠️  Archivo no encontrado: {migration_file}")
        
        conn.commit()
        print("✅ Todas las migraciones de productos creadas exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al ejecutar migraciones: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔧 Iniciando migración de productos...")
    create_productos_tables()
    print("✅ Migración completada")
