"""
Implementación PostgreSQL de UsuarioRepository.
Se integrará cuando se configure conexión real a BD.
"""

import psycopg2
from typing import List, Optional
from models.usuario import Usuario, RoleEnum
from repositories.usuario_repository import IUsuarioRepository
from datetime import datetime

class PostgreSQLUsuarioRepository(IUsuarioRepository):
    """Implementación PostgreSQL de UsuarioRepository"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def _get_connection(self):
        """Obtener conexión a BD"""
        return psycopg2.connect(self.connection_string)
    
    def create(self, email: str, password_hash: str, role: RoleEnum = RoleEnum.CUSTOMER) -> Usuario:
        """Crear nuevo usuario"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO usuarios (email, password_hash, role, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, email, password_hash, role, is_active, created_at, updated_at
                """,
                (email, password_hash, role.value, True, datetime.utcnow(), datetime.utcnow())
            )
            row = cursor.fetchone()
            conn.commit()
            
            if row:
                return Usuario(
                    id=row[0],
                    email=row[1],
                    password_hash=row[2],
                    role=RoleEnum(row[3]),
                    is_active=row[4],
                    created_at=row[5],
                    updated_at=row[6]
                )
        except psycopg2.IntegrityError as e:
            conn.rollback()
            raise ValueError(f"Email {email} ya registrado")
        finally:
            cursor.close()
            conn.close()
    
    def find_by_email(self, email: str) -> Optional[Usuario]:
        """Buscar usuario por email"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, email, password_hash, role, is_active, created_at, updated_at FROM usuarios WHERE email = %s",
                (email,)
            )
            row = cursor.fetchone()
            
            if row:
                return Usuario(
                    id=row[0],
                    email=row[1],
                    password_hash=row[2],
                    role=RoleEnum(row[3]),
                    is_active=row[4],
                    created_at=row[5],
                    updated_at=row[6]
                )
        finally:
            cursor.close()
            conn.close()
        
        return None
    
    def find_by_id(self, user_id: int) -> Optional[Usuario]:
        """Buscar usuario por id"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, email, password_hash, role, is_active, created_at, updated_at FROM usuarios WHERE id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return Usuario(
                    id=row[0],
                    email=row[1],
                    password_hash=row[2],
                    role=RoleEnum(row[3]),
                    is_active=row[4],
                    created_at=row[5],
                    updated_at=row[6]
                )
        finally:
            cursor.close()
            conn.close()
        
        return None
    
    def update(self, user_id: int, **kwargs) -> Optional[Usuario]:
        """Actualizar usuario"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Construir SET dinámicamente
            allowed_fields = {"email", "password_hash", "role", "is_active"}
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not updates:
                return self.find_by_id(user_id)
            
            set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [datetime.utcnow(), user_id]
            
            cursor.execute(
                f"UPDATE usuarios SET {set_clause}, updated_at = %s WHERE id = %s RETURNING id, email, password_hash, role, is_active, created_at, updated_at",
                values
            )
            row = cursor.fetchone()
            conn.commit()
            
            if row:
                return Usuario(
                    id=row[0],
                    email=row[1],
                    password_hash=row[2],
                    role=RoleEnum(row[3]),
                    is_active=row[4],
                    created_at=row[5],
                    updated_at=row[6]
                )
        finally:
            cursor.close()
            conn.close()
        
        return None
    
    def deactivate(self, user_id: int) -> bool:
        """Desactivar usuario"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE usuarios SET is_active = False, updated_at = %s WHERE id = %s",
                (datetime.utcnow(), user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    def list_all(self, limit: int = 100, offset: int = 0) -> List[Usuario]:
        """Listar todos los usuarios con paginación"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, email, password_hash, role, is_active, created_at, updated_at FROM usuarios LIMIT %s OFFSET %s",
                (limit, offset)
            )
            rows = cursor.fetchall()
            
            return [
                Usuario(
                    id=row[0],
                    email=row[1],
                    password_hash=row[2],
                    role=RoleEnum(row[3]),
                    is_active=row[4],
                    created_at=row[5],
                    updated_at=row[6]
                )
                for row in rows
            ]
        finally:
            cursor.close()
            conn.close()
