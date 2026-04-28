"""
Script de seed inicial para el backend Food Store.

Este script NO se debe ejecutar en producción.
Carga algunos datos de ejemplo para desarrollo en una base PostgreSQL.
"""

import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env', override=True)

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
    )

SEED_CAT = [
    (1, 'Bebidas', 'Gaseosas, jugos, aguas'),
    (2, 'Comidas', 'Platos principales, sándwiches, ensaladas'),
]

if __name__ == "__main__":
    if os.getenv('ENV', 'development') == 'production':
        print("ERROR: No se puede ejecutar seed en producción.")
        exit(1)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS categoria (id SERIAL PRIMARY KEY, nombre TEXT, descripcion TEXT);")
    cur.execute("DELETE FROM categoria;")
    cur.executemany("INSERT INTO categoria(id, nombre, descripcion) VALUES (%s, %s, %s);", SEED_CAT)
    conn.commit()
    cur.close()
    conn.close()
    print("Seed cargado OK en tabla categoria!")
