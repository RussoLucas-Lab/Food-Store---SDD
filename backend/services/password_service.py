"""
Servicio de seguridad de contraseñas usando bcrypt.
Maneja: hashing, verificación, validación de complejidad.
"""

import bcrypt
from typing import List
import re

class PasswordService:
    """Servicio para operaciones de contraseña segura"""
    
    # Requisitos de complejidad
    MIN_LENGTH = 8
    REQUIRE_UPPER = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*"
    
    @staticmethod
    def hash_password(plaintext: str) -> str:
        """
        Hashear contraseña con bcrypt.
        
        Args:
            plaintext: Contraseña en texto plano
            
        Returns:
            Hash bcrypt de la contraseña (string)
            
        Nota: Nunca loguear plaintext
        """
        # bcrypt.hashpw espera bytes, retorna bytes
        pwd_bytes = plaintext.encode('utf-8')
        hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plaintext: str, hash_value: str) -> bool:
        """
        Verificar contraseña contra hash.
        
        Args:
            plaintext: Contraseña en texto plano a verificar
            hash_value: Hash bcrypt guardado (string)
            
        Returns:
            True si coincide, False si no
            
        Nota: No loguear plaintext
        """
        pwd_bytes = plaintext.encode('utf-8')
        hash_bytes = hash_value.encode('utf-8') if isinstance(hash_value, str) else hash_value
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    
    @staticmethod
    def validate_password_strength(password: str) -> List[str]:
        """
        Validar fortaleza de contraseña.
        
        Args:
            password: Contraseña a validar
            
        Returns:
            Lista vacía si válida, lista de errores si inválida
            
        Requisitos:
            - Mínimo 8 caracteres
            - Al menos 1 mayúscula
            - Al menos 1 dígito
            - Al menos 1 carácter especial (!@#$%^&*)
        """
        errors = []
        
        # Validar largo
        if len(password) < PasswordService.MIN_LENGTH:
            errors.append(f"Password debe tener al menos {PasswordService.MIN_LENGTH} caracteres")
        
        # Validar mayúscula
        if PasswordService.REQUIRE_UPPER and not re.search(r'[A-Z]', password):
            errors.append("Password debe contener al menos una mayúscula (A-Z)")
        
        # Validar dígito
        if PasswordService.REQUIRE_DIGIT and not re.search(r'[0-9]', password):
            errors.append("Password debe contener al menos un dígito (0-9)")
        
        # Validar carácter especial
        if PasswordService.REQUIRE_SPECIAL:
            special_pattern = f"[{re.escape(PasswordService.SPECIAL_CHARS)}]"
            if not re.search(special_pattern, password):
                errors.append(f"Password debe contener al menos un carácter especial ({PasswordService.SPECIAL_CHARS})")
        
        return errors


# Instancia global del servicio
password_service = PasswordService()
