## Context

Actualmente el backend tiene estructura UoW + Repository pero sin autenticación ni control de acceso. El modelo Usuario existe solo con id y nombre. Necesitamos implementar un sistema de auth robusto que:
- Valide credenciales (email + contraseña)
- Emita tokens JWT seguros
- Aplique rate limiting contra fuerza bruta
- Permita validar roles en endpoints protegidos

El proyecto usa FastAPI como framework (confirmar en requirements), PostgreSQL como BD, y Python 3.9+.

## Goals / Non-Goals

**Goals:**
- Implementar endpoints REST seguros: `/auth/register`, `/auth/login`, `/auth/me`
- Usar JWT con access_token + refresh_token (modelo industry-standard)
- Proteger contraseñas con bcrypt mediante Passlib
- Rate limit login a 5 intentos / 15 min por IP
- Validar roles con decoradores (`@require_role("admin")`)
- Integrar con Unit of Work existente para persistencia de Usuario
- Documentar contratos públicos (schemas de request/response)

**Non-Goals:**
- OAuth social (Google, GitHub, etc.) — solo email/password
- 2FA multi-factor — alcance posterior
- Auditoría detallada de login attempts — solo rate limiting
- Migración de usuarios existentes
- Refresh token rotation strategy — simplificar: usar expiration

## Decisions

### 1. **JWT con acceso + refresh separados**
**Decision**: `access_token` (15 min) + `refresh_token` (7 días)
**Why**: Limita exposición si se roba el access_token. Estándar industry (OAuth 2.0).
**Alternatives**:
- Single JWT largo plazo: más simple pero arriesgado si se roba
- Session-based (cookies): requiere backend stateful, incompatible con microservicios

### 2. **Almacenamiento de refresh_token**
**Decision**: En memoria (Redis opcional después) con invalidación en logout
**Why**: Simplifica fase inicial, evita complejidad de table de tokens
**Alternatives**:
- DB table con tokens: más robusto pero mayor overhead
- Solo revoke en logout (discard token del cliente): inseguro si se roban tokens

### 3. **Rate limiting: slowapi en endpoint /login**
**Decision**: 5 intentos / 15 min por IP, usando slowapi middleware
**Why**: Protege contra ataques de fuerza bruta sin complejidad
**Alternatives**:
- Implementar manualmente con Redis counters: overhead innecesario
- Sin rate limiting: vulnerable

### 4. **Estructura de carpetas backend**
```
backend/
├── main.py                      # FastAPI app
├── requirements.txt
├── routers/
│   └── auth.py                 # Endpoints: /auth/*
├── schemas/
│   ├── auth_schema.py          # Pydantic: LoginRequest, TokenResponse
│   └── user_schema.py          # UserOut, UserCreate
├── services/
│   ├── auth_service.py         # Lógica de login, register, token validation
│   └── password_service.py     # Hash, verify con Passlib
├── middleware/
│   └── jwt_middleware.py       # Extraer y validar JWT de requests
└── models/
    └── usuario.py              # (ya existe, expandir con email, password_hash, role, status)
```

### 5. **Modelo Usuario expandido**
```python
class Usuario:
    id: int                      # PK
    email: str (unique, not null)
    password_hash: str           # Passlib/bcrypt
    role: Enum("admin", "customer")
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
```

### 6. **Validación de contraseña**
**Decision**: Validación básica en Pydantic (min 8 chars, 1 upper, 1 digit, 1 special)
**Why**: Previene contraseñas débiles sin complejidad excesiva
**Alternatives**:
- Sin validación: inseguro
- Validación extrema (NIST SP 800-63): overkill para fase 1

### 7. **Token Claims (JWT payload)**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "admin" | "customer",
  "exp": 1234567890,
  "iat": 1234567200
}
```

### 8. **Autenticación vs Autorización**
- **Autenticación**: Verificar quién eres (login/token validation)
- **Autorización**: Verificar qué puedes hacer (role-based)
- Ambas se validan en middleware y decoradores

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Token robado = acceso total | Usar access_token corto (15 min), invalidar refresh en logout |
| Rate limiting evitable por múltiples IPs | Aceptable para MVP, escalar con CAPTCHA después |
| Contraseña débil memorizada insegura | Validación Pydantic + email de confirmación (later) |
| Secret key comprometida | Almacenar en `.env` no versionado, rotación manual |
| Token sin expiración (eterno) | Siempre con exp, refresh_token también expira |
| Información sensitiva en logs | NO loguear contraseñas ni tokens completos |

## Migration Plan

**Paso 1**: Crear DB schema de usuarios (tabla con columnas)
**Paso 2**: Expandir modelo Usuario con email, password_hash, role, status
**Paso 3**: Implementar servicios (hash, token generation)
**Paso 4**: Implementar endpoints (/register, /login, /me, /logout)
**Paso 5**: Implementar middleware y decoradores de validación
**Paso 6**: Tests unitarios de auth_service, endpoint tests
**Paso 7**: Documentar en OpenAPI (FastAPI auto-genera)

## Open Questions

- ¿Confirmación de email en registro o inmediato?
- ¿Endpoint /logout marca token como inválido o simplemente cliente descarta?
- ¿Roles se guardan en JWT o se validan desde DB en cada request?
- ¿Estructura de permisos: solo roles o granular (permisos x rol)?
