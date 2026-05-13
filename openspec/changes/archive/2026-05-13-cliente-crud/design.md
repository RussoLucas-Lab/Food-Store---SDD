## Context

El sistema Food Store ya tiene establecido un patrón arquitectónico: **Repository + UoW (Unit of Work) + Service Layer**. Este patrón se aplicó exitosamente en `categoria-crud`, `ingrediente-crud` y `producto-crud`. El cliente es una entidad fundamental que será referenciada por `carrito-pedidos` (próximo change), por eso debe estar sólido.

Actualmente, no existe modelo Cliente en el sistema. Auth maneja usuarios (auth_user), pero Cliente es una entidad de dominio separada con datos específicos del negocio (dirección, teléfono, etc.).

## Goals / Non-Goals

**Goals:**
- Implementar CRUD completo de clientes con el patrón existente (Repository + UoW + Service)
- Validar datos únicos (email) y requeridos
- Soft-delete: marcar clientes como inactivos, nunca borrar BD
- Control de acceso por roles: admin ve todos, usuario normal solo su perfil
- Backend y frontend funcionando juntos (React consume la API)
- 100% cobertura de tests (unit + integration + schema validation)

**Non-Goals:**
- Integración con OAuth o proveedores externos (autenticación ya existe en auth-roles)
- Notificaciones por email (despacho-pedidos lo maneja)
- Importación masiva de clientes (será manual)
- Auditoría de cambios (no es requisito core)

## Decisions

### 1. Estructura de Datos: Cliente separado de auth_user
**Decisión:** Crear tabla `clientes` independiente de `auth_user`, relacionada por user_id (opcional).
**Rationale:** 
- Un usuario puede no ser cliente (ej: admin)
- Un cliente puede tener campos específicos del dominio (dirección de entrega, teléfono de contacto)
- Flexibilidad: clientes sin cuenta activa (ej: datos importados)

**Alternativas consideradas:**
- Extender auth_user con campos cliente → Couples domain logic to auth, hard to refactor
- Solo usar auth_user como cliente → No soporta clientes sin cuenta

### 2. Validación de Email Único a Nivel BD
**Decisión:** UNIQUE constraint en BD + validación Pydantic en el service.
**Rationale:**
- Race conditions: dos requests simultáneos sin constraint BD fallarían
- Integridad garantizada

### 3. Soft Delete con Campo `activo: bool`
**Decisión:** Agregar `activo: bool` (default True), queries excluyen `activo=False` por defecto.
**Rationale:**
- Consistente con categoria-crud e ingrediente-crud
- Preserva histórico (pedidos referenciados siguen teniendo datos)
- Reversible: reactivar cliente es simple UPDATE

### 4. Control de Acceso: Rol Basado
**Decisión:** 
- `ADMIN`: puede ver/editar/borrar cualquier cliente
- `USER` (cliente): puede ver/editar solo SU perfil, no otros
- `GUEST`: sin acceso
**Rationale:** Protege privacidad de datos, permite que admins gestionen base de clientes.

### 5. Endpoints REST (7 operaciones)
**Decisión:**
- `POST /clientes` → crear cliente (solo ADMIN)
- `GET /clientes` → listar todos (ADMIN), o listar solo el propio (USER)
- `GET /clientes/{id}` → obtener cliente (ADMIN o el dueño)
- `PATCH /clientes/{id}` → editar cliente (ADMIN o el dueño)
- `DELETE /clientes/{id}` → soft-delete (solo ADMIN)
- `GET /clientes/search?q=...` → buscar por nombre/email (ADMIN)
- `PATCH /clientes/{id}/reactivar` → reactivar (solo ADMIN)

**Rationale:** CRUD REST estándar + búsqueda + reactivación.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| **Email duplicado en alta carga** | UNIQUE constraint BD + retry logic en service |
| **Referencia de cliente borrado en pedidos** | Soft-delete preserva datos, queries filtran por `activo=True` |
| **User confunde su perfil con todos los clientes** | Frontend muestra UI diferente según rol; tests validan acceso |
| **Mucho código duplicado con categoria/ingrediente** | Usar templates/base classes (Repository<T>, Service<T>) en refactor futuro |

## Migration Plan

1. **Crear tabla `clientes`** con schema: id, name, email, phone, address, active, created_at, updated_at, user_id (nullable)
2. **Implementar layers**: Models → Repository → Service → Schemas → Endpoints
3. **Tests**: Unit (service), Integration (API), Schema validation
4. **Frontend**: Componentes React para CRUD, ruteo, llamadas HTTP
5. **Seed DB**: Datos de prueba (clientes pre-cargados)
6. **Documentación API**: Docstrings Pydantic, comentarios en endpoints

**Rollback:** Eliminar tabla `clientes` y endpoints (cambio es aislado, no afecta resto del sistema).
