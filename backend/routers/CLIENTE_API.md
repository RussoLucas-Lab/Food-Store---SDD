"""
# Cliente API Endpoints Documentation

## Base URL
`/api` or `http://localhost:8000`

## Authentication
All endpoints require JWT token in `Authorization` header:
```
Authorization: Bearer <token>
```

---

## Endpoints

### 1. CREATE Cliente
**Endpoint**: `POST /clientes`
**Auth**: Required (ADMIN only)
**Rate Limit**: 5 req/15 min

**Request**:
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "telefono": "+54 11 1234 5678",
  "direccion": "Calle Principal 123, Buenos Aires"
}
```

**Response (201)**:
```json
{
  "id": "uuid-123",
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "telefono": "+54 11 1234 5678",
  "direccion": "Calle Principal 123, Buenos Aires",
  "activo": true,
  "created_at": "2026-05-13T10:30:00Z",
  "updated_at": "2026-05-13T10:30:00Z",
  "user_id": null
}
```

**Errors**:
- `400`: Email already exists, invalid format, required fields missing
- `401`: Unauthorized (no token)
- `403`: Forbidden (not ADMIN)

---

### 2. LIST Clientes
**Endpoint**: `GET /clientes?page=1&limit=10`
**Auth**: Required
**Rate Limit**: 5 req/15 min

**Query Parameters**:
- `page`: int (default: 1)
- `limit`: int (default: 10, max: 100)

**Response (200)**:
```json
{
  "items": [
    {
      "id": "uuid-123",
      "nombre": "Juan Pérez",
      "email": "juan@example.com",
      "telefono": "+54 11 1234 5678",
      "direccion": "Calle Principal 123, Buenos Aires",
      "activo": true,
      "created_at": "2026-05-13T10:30:00Z",
      "updated_at": "2026-05-13T10:30:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 10
}
```

**Role-based behavior**:
- ADMIN: returns all active clientes
- USER: returns only their own profile
- GUEST: 401 Unauthorized

**Errors**:
- `401`: Unauthorized (no token, expired)

---

### 3. GET Cliente by ID
**Endpoint**: `GET /clientes/{id}`
**Auth**: Required
**Rate Limit**: 5 req/15 min

**Path Parameters**:
- `id`: string (UUID of cliente)

**Response (200)**:
```json
{
  "id": "uuid-123",
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "telefono": "+54 11 1234 5678",
  "direccion": "Calle Principal 123, Buenos Aires",
  "activo": true,
  "created_at": "2026-05-13T10:30:00Z",
  "updated_at": "2026-05-13T10:30:00Z"
}
```

**Role-based access**:
- ADMIN: can view any cliente
- USER: can view only own profile
- Trying to view other's profile: 403 Forbidden

**Errors**:
- `401`: Unauthorized
- `403`: Forbidden (not owner, not admin)
- `404`: Cliente not found

---

### 4. UPDATE Cliente
**Endpoint**: `PATCH /clientes/{id}`
**Auth**: Required
**Rate Limit**: 5 req/15 min

**Request** (partial update):
```json
{
  "nombre": "Juan Manuel Pérez",
  "email": "juan.manual@example.com",
  "telefono": "+54 11 5555 5555",
  "direccion": "Calle Nueva 456"
}
```

**Response (200)**:
```json
{
  "id": "uuid-123",
  "nombre": "Juan Manuel Pérez",
  "email": "juan.manual@example.com",
  "telefono": "+54 11 5555 5555",
  "direccion": "Calle Nueva 456",
  "activo": true,
  "created_at": "2026-05-13T10:30:00Z",
  "updated_at": "2026-05-13T10:35:00Z"
}
```

**Role-based access**:
- ADMIN: can update any cliente
- USER: can update only own profile
- Trying to update other's: 403 Forbidden

**Validations**:
- Email: unique, valid format
- Name: min 3 chars, max 255
- Phone: min 10 chars, max 20
- Address: required, max 500 chars

**Errors**:
- `400`: Validation error (email duplicate, format invalid)
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Cliente not found
- `409`: Conflict (email already exists for other cliente)

---

### 5. SOFT DELETE Cliente
**Endpoint**: `DELETE /clientes/{id}`
**Auth**: Required (ADMIN only)
**Rate Limit**: 5 req/15 min

**Path Parameters**:
- `id`: string (UUID of cliente)

**Response (200)**:
```json
{
  "id": "uuid-123",
  "message": "Cliente eliminado exitosamente"
}
```

**Behavior**:
- Sets `activo = false` (soft delete)
- Data is preserved in DB
- Excluded from LIST queries
- Can be reactivated with PUT /clientes/{id}/reactivar

**Errors**:
- `401`: Unauthorized
- `403`: Forbidden (only ADMIN can delete)
- `404`: Cliente not found

---

### 6. REACTIVATE Cliente
**Endpoint**: `PATCH /clientes/{id}/reactivar`
**Auth**: Required (ADMIN only)
**Rate Limit**: 5 req/15 min

**Path Parameters**:
- `id`: string (UUID of cliente)

**Response (200)**:
```json
{
  "id": "uuid-123",
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "telefono": "+54 11 1234 5678",
  "direccion": "Calle Principal 123, Buenos Aires",
  "activo": true,
  "created_at": "2026-05-13T10:30:00Z",
  "updated_at": "2026-05-13T10:40:00Z"
}
```

**Behavior**:
- Sets `activo = true`
- Cliente reappears in LIST
- Only works on soft-deleted clientes

**Errors**:
- `401`: Unauthorized
- `403`: Forbidden (only ADMIN can reactivate)
- `404`: Cliente not found

---

### 7. SEARCH Clientes
**Endpoint**: `GET /clientes/search?q=<query>`
**Auth**: Required (ADMIN only)
**Rate Limit**: 5 req/15 min

**Query Parameters**:
- `q`: string (search term: name or email)

**Response (200)**:
```json
[
  {
    "id": "uuid-123",
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "telefono": "+54 11 1234 5678",
    "direccion": "Calle Principal 123, Buenos Aires",
    "activo": true
  },
  {
    "id": "uuid-456",
    "nombre": "Juan Carlos López",
    "email": "juancarlos@example.com",
    "telefono": "+54 11 9999 9999",
    "direccion": "Avenida Siempreviva 742",
    "activo": true
  }
]
```

**Search behavior**:
- Searches in: `nombre` AND `email`
- Case-insensitive
- Partial match (LIKE)
- Returns only active clientes
- ADMIN only

**Errors**:
- `400`: Query too short (min 2 chars)
- `401`: Unauthorized
- `403`: Forbidden (only ADMIN)

---

## Error Response Format

All errors follow this format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "status": 400,
  "details": {
    "field": "email",
    "message": "Email already exists"
  }
}
```

**Common Error Codes**:
- `VALIDATION_ERROR`: Input validation failed
- `UNIQUE_CONSTRAINT`: Duplicate unique field
- `NOT_FOUND`: Resource doesn't exist
- `PERMISSION_DENIED`: Access denied
- `RATE_LIMIT`: Too many requests
- `INTERNAL_ERROR`: Server error (5xx)

---

## HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success (no body)
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing/invalid token
- `403 Forbidden`: No permission for action
- `404 Not Found`: Resource not found
- `409 Conflict`: Constraint violation (e.g., duplicate email)
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## Usage Examples

### Create cliente with curl
```bash
curl -X POST http://localhost:8000/clientes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "telefono": "+54 11 1234 5678",
    "direccion": "Calle Principal 123"
  }'
```

### Search clientes
```bash
curl http://localhost:8000/clientes/search?q=juan \
  -H "Authorization: Bearer <token>"
```

### Update cliente
```bash
curl -X PATCH http://localhost:8000/clientes/uuid-123 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan.nuevo@example.com",
    "telefono": "+54 11 9999 9999"
  }'
```

### Delete cliente
```bash
curl -X DELETE http://localhost:8000/clientes/uuid-123 \
  -H "Authorization: Bearer <token>"
```

---

## Rate Limiting

- Limit: 5 requests per 15 minutes per IP
- Header: `X-RateLimit-Remaining`
- On limit exceeded: `429 Too Many Requests`

---

## Pagination

All list endpoints support pagination:
- Default page size: 10
- Max page size: 100
- Response includes: `total`, `page`, `limit`

Example:
```
GET /clientes?page=2&limit=20
```

---

## Soft Delete

Clientes are never permanently deleted:
1. DELETE sets `activo = false`
2. GET and LIST exclude inactive clientes
3. Can reactivate with PATCH /clientes/{id}/reactivar
4. Pedidos that reference deleted clientes still work
"""
