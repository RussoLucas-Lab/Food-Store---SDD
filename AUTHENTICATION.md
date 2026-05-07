# Autenticación y Control de Acceso — Food Store API

Esta documentación describe el sistema de autenticación JWT y control de acceso basado en roles (RBAC) implementado en Food Store.

---

## Descripción General

El sistema de autenticación de Food Store usa:
- **JWT (JSON Web Tokens)** con algoritmo HS256
- **Refresh tokens** para renovar acceso sin volver a hacer login
- **Bcrypt** para hashing seguro de contraseñas
- **Rate limiting** para proteger endpoints de login contra ataques de fuerza bruta
- **RBAC** con dos roles: `admin` y `customer`

---

## Flujo de Autenticación

```
┌─────────────────────────────────────────────────────────────┐
│                   AUTH FLOW                                 │
└─────────────────────────────────────────────────────────────┘

1. REGISTRO
   POST /auth/register
   {email, password}
   ↓
   ✓ Validar email único
   ✓ Validar fortaleza de contraseña
   ✓ Hash con bcrypt
   → Retorna Usuario (id, email, role=customer, is_active=true)

2. LOGIN
   POST /auth/login
   {email, password}
   ↓
   ✓ Buscar usuario por email
   ✓ Verificar contraseña contra hash
   ✓ Generar access_token (15 min) + refresh_token (7 días)
   → Retorna {access_token, refresh_token, expires_in=900}

3. USAR TOKEN
   GET /api/protected
   Headers: Authorization: Bearer <access_token>
   ↓
   ✓ Validar firma JWT
   ✓ Verificar exp < now
   ✓ Extraer user_id, email, role
   ✓ Validar role vs endpoint @require_role()
   → Permitir o negar acceso

4. RENOVAR TOKEN (opcional)
   POST /auth/refresh
   {refresh_token}
   ↓
   ✓ Validar que refresh_token no haya sido revocado
   ✓ Generar nuevo access_token
   → Retorna {access_token, refresh_token, expires_in=900}

5. LOGOUT
   POST /auth/logout
   Headers: Authorization: Bearer <access_token>
   ↓
   ✓ Revocar refresh_token (invalidar para futures refresh)
   → Mensaje de éxito
```

---

## Endpoints de Autenticación

### 1. Registro

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Respuesta (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "nombre": "user",
  "role": "customer",
  "is_active": true,
  "created_at": "2026-05-06T10:00:00",
  "updated_at": "2026-05-06T10:00:00"
}
```

**Errores:**
- `400 Bad Request`: Email ya registrado, contraseña débil
- `422 Unprocessable Entity`: Email inválido, datos faltantes

---

### 2. Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Respuesta (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

**Errores:**
- `401 Unauthorized`: Credenciales inválidas, usuario inactivo
- `429 Too Many Requests`: Rate limit excedido (> 5 intentos / 15 min)

---

### 3. Obtener Perfil Actual

```http
GET /auth/me
Authorization: Bearer <access_token>
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "nombre": "user",
  "role": "customer",
  "is_active": true,
  "created_at": "2026-05-06T10:00:00",
  "updated_at": "2026-05-06T10:00:00"
}
```

**Errores:**
- `401 Unauthorized`: Token missing, invalid, or expired

---

### 4. Renovar Token

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Respuesta (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

**Errores:**
- `401 Unauthorized`: Refresh token inválido, expirado o revocado

---

### 5. Logout

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

**Respuesta (200 OK):**
```json
{
  "message": "Logged out successfully",
  "status": "ok"
}
```

**Errores:**
- `401 Unauthorized`: Token missing or invalid

---

## Estructura JWT

### Access Token

```json
{
  "sub": "1",                    // user_id
  "email": "user@example.com",
  "role": "customer",            // "admin" | "customer"
  "exp": 1234567890,            // expiration timestamp
  "iat": 1234567200,            // issued-at timestamp
  "type": "access"
}
```

**Duración:** 15 minutos (configurable en `.env`: `ACCESS_TOKEN_EXPIRE_MINUTES`)

### Refresh Token

```json
{
  "sub": "1",                    // user_id
  "exp": 1234567890,
  "iat": 1234567200,
  "type": "refresh"
}
```

**Duración:** 7 días (configurable en `.env`: `REFRESH_TOKEN_EXPIRE_DAYS`)

---

## Roles y Permisos

### Admin

- ✅ Acceso total a todas las operaciones
- ✅ Crear, editar, eliminar productos, categorías, ingredientes
- ✅ Ver pedidos de cualquier cliente
- ✅ Gestionar usuarios
- ✅ Acceder a panel administrativo

Endpoints: `@require_role("admin")`

### Customer

- ✅ Ver catálogo de productos
- ✅ Crear y gestionar propios pedidos
- ✅ Ver propios pedidos y estado
- ✅ Actualizar perfil personal
- ❌ No puede crear/editar productos
- ❌ No puede ver pedidos de otros
- ❌ No puede acceder a panel admin

Endpoints: Sin decorador (público autenticado) o `@require_role("customer")`

---

## Validación de Contraseña

Las contraseñas deben cumplir:

- ✅ Mínimo 8 caracteres
- ✅ Al menos 1 mayúscula (A-Z)
- ✅ Al menos 1 dígito (0-9)
- ✅ Al menos 1 carácter especial (!@#$%^&*)

Ejemplo válido: `SecurePass123!`  
Ejemplo inválido: `weak` (no cumple ningún requisito)

---

## Rate Limiting

El endpoint `/auth/login` está protegido contra ataques de fuerza bruta:

- **Límite**: 5 intentos cada 15 minutos
- **Agrupación**: Por dirección IP del cliente

Respuesta cuando se excede:
```json
{
  "error": "Rate limit exceeded: 5 attempts per 15 minutes"
}
Status: 429 Too Many Requests
Header: Retry-After: 120
```

---

## Variables de Entorno

Crear `.env` en la raíz del proyecto:

```env
# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=devuser
DB_PASS=devpass
DB_NAME=foodstore_dev

# Environment
ENV=development
```

**Importante:** Cambiar `SECRET_KEY` en producción (mínimo 32 caracteres aleatorios)

---

## Integración en Endpoints

### Endpoint público autenticado (solo requiere token válido)

```python
from fastapi import APIRouter, Depends
from backend.middleware.jwt_middleware import get_current_user, CurrentUser

router = APIRouter()

@router.get("/public-auth")
async def public_endpoint(current_user: CurrentUser = Depends(get_current_user)):
    return {
        "message": f"Hello {current_user.email}",
        "role": current_user.role
    }
```

### Endpoint solo para admin

```python
from backend.middleware.jwt_middleware import require_role, get_current_user

@router.post("/admin/users")
@require_role("admin")
async def admin_endpoint(current_user: CurrentUser = Depends(get_current_user)):
    return {"message": "Admin-only operation"}
```

### Endpoint solo para customer

```python
@router.post("/orders")
@require_role("customer")
async def create_order(current_user: CurrentUser = Depends(get_current_user)):
    return {"user_id": current_user.user_id, "order": "..."}
```

---

## Testing Manual

### Con curl

```bash
# 1. Registro
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }' | jq '.access_token'

# 3. Usar token (reemplazar con token real)
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 4. Logout
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Con Postman

1. Ir a `http://localhost:8000/docs` (Swagger UI)
2. Expandir `/auth/register` → "Try it out" → completar email + password → "Execute"
3. Copiar `access_token` del response
4. Expandir `/auth/me` → Click en botón "Authorize" (arriba a derecha) → Ingresar token → "Authorize"
5. Ejecutar `/auth/me`

---

## Seguridad

### ✅ Lo que hacemos bien

- Contraseñas hasheadas con bcrypt (nunca almacenamos plaintext)
- Tokens JWT firmados con HS256
- Access tokens de corta vida (15 min) + refresh tokens revocables
- Rate limiting en login (5 intentos / 15 min)
- Validación de complejidad de contraseña
- Password hash nunca se expone en responses

### ⚠️ Consideraciones para Producción

- Cambiar `SECRET_KEY` a string aleatorio de 32+ chars
- Usar HTTPS en producción (no HTTP)
- Configurar CORS apropiadamente (whitelist de dominios)
- Implementar CSRF protection si se usan cookies
- Considerar 2FA para usuarios admin
- Implementar logout masivo (token blacklist en Redis)
- Auditoría de intentos fallidos de login

---

## Recursos

- Especificaciones del change: `openspec/changes/auth-roles/specs/`
- Diseño técnico: `openspec/changes/auth-roles/design.md`
- Propuesta: `openspec/changes/auth-roles/proposal.md`
- Tests: `tests/test_auth_*.py`
