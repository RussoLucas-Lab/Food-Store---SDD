"""
Tests para PasswordService (ahora en backend.core.security)
"""

import pytest
from backend.core.security import PasswordService


class TestPasswordService:

    def test_hash_password_creates_bcrypt_hash(self):
        """Hash debe crear un bcrypt válido"""
        plaintext = "SecurePass123!"
        hashed = PasswordService.hash_password(plaintext)

        assert hashed.startswith("$2b$")  # Patrón bcrypt
        assert len(hashed) >= 60
        assert hashed != plaintext

    def test_hash_different_salts(self):
        """Hashes de misma contraseña deben ser diferentes (salts diferentes)"""
        plaintext = "SecurePass123!"
        hash1 = PasswordService.hash_password(plaintext)
        hash2 = PasswordService.hash_password(plaintext)

        assert hash1 != hash2  # Diferentes salts
        assert PasswordService.verify_password(plaintext, hash1)
        assert PasswordService.verify_password(plaintext, hash2)

    def test_verify_password_success(self):
        """Verificación debe pasar con contraseña correcta"""
        plaintext = "SecurePass123!"
        hashed = PasswordService.hash_password(plaintext)

        assert PasswordService.verify_password(plaintext, hashed) is True

    def test_verify_password_failure(self):
        """Verificación debe fallar con contraseña incorrecta"""
        plaintext = "SecurePass123!"
        hashed = PasswordService.hash_password(plaintext)
        wrong = "WrongPass456!"

        assert PasswordService.verify_password(wrong, hashed) is False

    def test_validate_strong_password(self):
        """Contraseña fuerte debe pasar validación"""
        strong_password = "Secure@Pass123"
        errors = PasswordService.validate_password_strength(strong_password)

        assert errors == []

    def test_validate_weak_password_too_short(self):
        """Contraseña muy corta debe fallar"""
        weak = "Pass1!"
        errors = PasswordService.validate_password_strength(weak)

        assert len(errors) > 0
        assert any("8 caracteres" in err for err in errors)

    def test_validate_weak_password_no_uppercase(self):
        """Contraseña sin mayúscula debe fallar"""
        weak = "secure@pass123"
        errors = PasswordService.validate_password_strength(weak)

        assert len(errors) > 0
        assert any("mayúscula" in err for err in errors)

    def test_validate_weak_password_no_digit(self):
        """Contraseña sin dígito debe fallar"""
        weak = "SecurePass@abc"
        errors = PasswordService.validate_password_strength(weak)

        assert len(errors) > 0
        assert any("dígito" in err for err in errors)

    def test_validate_weak_password_no_special(self):
        """Contraseña sin carácter especial debe fallar"""
        weak = "SecurePass123"
        errors = PasswordService.validate_password_strength(weak)

        assert len(errors) > 0
        assert any("especial" in err for err in errors)

    def test_validate_multiple_issues(self):
        """Contraseña con múltiples problemas"""
        weak = "pass"
        errors = PasswordService.validate_password_strength(weak)

        # Debe reportar múltiples errores
        assert len(errors) >= 3

    def test_password_never_in_hash_comparison(self):
        """Verificar que plaintext no se expone"""
        plaintext = "MySecurePass123!"
        hashed = PasswordService.hash_password(plaintext)

        # Plaintext no debe aparecer en el hash
        assert plaintext not in hashed

        # Pero debe verificar correctamente
        assert PasswordService.verify_password(plaintext, hashed)
