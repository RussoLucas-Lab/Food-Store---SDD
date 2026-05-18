# Food Store — Contexto del Proyecto para Claude Code

## ¿Qué es este proyecto?

Sistema de e-commerce de alimentos desarrollado como Trabajo Práctico Integrador (TPI) académico.
Permite a clientes explorar un catálogo, gestionar un carrito, realizar pedidos y pagar vía MercadoPago.
Los administradores gestionan catálogo, stock, pedidos y métricas desde un panel centralizado.

Metodología: **Spec-Driven Development (SDD)** con OPSX. Versión de spec: **v5.0**.
Documentación fuente de verdad: `docs/Descripcion.txt`, `docs/Integrador.txt`, `docs/Historias_de_usuario.txt`.

---

## Stack tecnológico

**Backend**: FastAPI · SQLModel · PostgreSQL 15+ · Alembic · Passlib/bcrypt · python-jose · slowapi · MercadoPago SDK Python  
**Frontend**: React 18 + TypeScript 5 · Vite 5 · TanStack Query v5 · TanStack Form · Zustand 4 · Axios · Tailwind CSS 3 · recharts · @mercadopago/sdk-react

---

## Arquitectura del backend

Capas con flujo de dependencias **estrictamente unidireccional**. Ninguna capa importa de la superior.

```
Router → Service → Unit of Work → Repository → Model
```

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Router | `router.py` | HTTP puro: parsear request, validar schema Pydantic, delegar al Service. **Sin lógica de negocio.** |
| Service | `service.py` | Lógica de negocio stateless. Orquesta via UoW. Lanza HTTPException. **Sin commit/rollback directo.** |
| Unit of Work | `core/uow.py` | Gestiona transacción: abre sesión, provee repos, hace commit() o rollback() automático. |
| Repository | `repository.py` | Acceso a BD sin lógica de negocio. Hereda `BaseRepository[T]`. Recibe sesión del UoW. |
| Model | `model.py` | Tablas SQLModel. Sin imports de capas superiores. |

Organización: **feature-first** (módulos por dominio, no por tipo técnico).

Módulos backend en `app/modules/`:
`auth/` · `refreshtokens/` · `usuarios/` · `direcciones/` · `categorias/` · `productos/` · `pedidos/` · `pagos/` · `admin/`

---

## Arquitectura del frontend

Patrón **Feature-Sliced Design (FSD)**. Imports fluyen de arriba hacia abajo, sin cross-imports entre features.

```
Pages → Features → Hooks/Stores → API → Types
```

Features principales: `auth/` · `store/` (catálogo/carrito/checkout) · `pedidos/` · `admin/`

**Separación estricta de estado:**
- **Zustand**: estado del cliente (carrito, sesión, proceso de pago, UI)
- **TanStack Query**: estado del servidor (productos, pedidos, dashboard)
- Mezclar ambos en un mismo store es un error arquitectónico.

### 4 Stores Zustand

| Store | Persiste | Qué gestiona |
|-------|----------|--------------|
| `authStore` | Sí (solo accessToken) | accessToken, usuario, isAuthenticated |
| `cartStore` | Sí (items completos) | ítems del carrito, cantidades, personalizaciones |
| `paymentStore` | No | Estado del proceso de pago MP: status, mpPaymentId |
| `uiStore` | No | cartOpen, sidebarOpen, confirmModal |

**Regla**: nunca `const store = useCartStore()` sin selector. Siempre `useCartStore(s => s.items)`.

---

## Modelo de datos — ERD v5

3NF · Soft Delete (`deleted_at TIMESTAMPTZ`) · Snapshot Pattern · Audit Trail append-only.

### Dominio 1 — Identidad y Acceso
`Usuario` · `Rol` (PK semántica: ADMIN/STOCK/PEDIDOS/CLIENT) · `UsuarioRol` (M2M) · `RefreshToken` · `DireccionEntrega`

### Dominio 2 — Catálogo
`Categoria` (jerarquía autoreferencial, CTE recursiva) · `Producto` (precio DECIMAL, stock INTEGER ≥ 0, disponible BOOLEAN) · `Ingrediente` (es_alergeno) · `ProductoCategoria` (M2M) · `ProductoIngrediente` (M2M, es_removible) · `FormaPago` (PK semántica: MERCADOPAGO/EFECTIVO/TRANSFERENCIA)

### Dominio 3 — Ventas y Pagos
`EstadoPedido` (es_terminal) · `Pedido` (total + costo_envio snapshots) · `DetallePedido` (nombre_snapshot, precio_snapshot, personalizacion INTEGER[]) · `HistorialEstadoPedido` (append-only, estado_desde NULL en primer registro) · `Pago` (mp_payment_id, mp_status, external_reference UQ, idempotency_key UQ)

---

## Máquina de estados del pedido (FSM)

```
PENDIENTE → CONFIRMADO → EN_PREP → EN_CAMINO → ENTREGADO (terminal)
     ↘           ↘          ↘
                         CANCELADO (terminal)
```

| Transición | Quién | Cuándo |
|-----------|-------|--------|
| PENDIENTE → CONFIRMADO | **Sistema** (automático) | Pago aprobado por MercadoPago |
| CONFIRMADO → EN_PREP | PEDIDOS / ADMIN | Manual |
| EN_PREP → EN_CAMINO | PEDIDOS / ADMIN | Manual |
| EN_CAMINO → ENTREGADO | PEDIDOS / ADMIN | Manual |
| PENDIENTE → CANCELADO | Cliente / PEDIDOS / ADMIN | Manual |
| CONFIRMADO → CANCELADO | PEDIDOS / ADMIN | Manual, restaura stock |
| EN_PREP → CANCELADO | **Solo ADMIN** | Manual, restaura stock |

**Reglas clave:**
- RN-FS01: No se permiten saltos ni retrocesos.
- RN-FS02: PENDIENTE→CONFIRMADO es exclusivamente automática. Nadie la ejecuta manual.
- RN-FS03: Al confirmar → decrementar stock de forma atómica.
- RN-FS05: Al cancelar un pedido confirmado → restaurar stock de forma atómica.
- RN-FS06: ENTREGADO y CANCELADO son terminales. Ninguna transición adicional.
- RN-FS07: `HistorialEstadoPedido` es **append-only**: solo INSERT, nunca UPDATE ni DELETE.
- RN-FS08: Cancelación desde EN_PREP solo posible para ADMIN.
- RN-PE05: motivo obligatorio si nuevo_estado = CANCELADO.

---

## Autenticación y autorización

**JWT** con HS256. Access token: 30 min. Refresh token: 7 días (UUID v4 opaco en BD).

- Al usar refresh token → rotación: revoca el anterior, emite uno nuevo.
- Rate limiting en login: 5 intentos/IP en 15 min → HTTP 429.
- Al registrarse → se asigna rol CLIENT automáticamente (nunca viene del request).
- Respuesta de login NO diferencia "email no existe" de "contraseña incorrecta" (seguridad).
- Datos de tarjeta NUNCA pasan por el servidor (PCI DSS SAQ-A, tokenización via SDK en browser).

### Roles RBAC

| Rol | Código | Permisos |
|-----|--------|----------|
| Administrador | ADMIN | CRUD completo, asigna roles |
| Gestor de Stock | STOCK | Catálogo e inventario únicamente |
| Gestor de Pedidos | PEDIDOS | Ver y avanzar pedidos únicamente |
| Cliente | CLIENT | Sus propios datos: carrito, pedidos, direcciones |

---

## API REST

Prefijo: `/api/v1`. Errores: RFC 7807. Paginación: `?page=1&size=20`.

Módulos principales: `auth` · `productos` · `categorias` · `ingredientes` · `pedidos` · `pagos` · `usuarios` · `direcciones` · `admin`

Convenciones de schemas Pydantic v2: siempre schemas separados `Create` / `Update` / `Read`. Nunca exponer el model SQLModel directamente como response.

---

## Integración MercadoPago

SDK Python en backend + `@mercadopago/sdk-react` en frontend.

Flujo:
1. Frontend tokeniza tarjeta con SDK (datos nunca tocan el servidor).
2. Backend crea pago con `idempotency_key` UUID.
3. MercadoPago envía webhook IPN a `POST /api/v1/pagos/webhook`.
4. Backend verifica estado real consultando API de MP (nunca confiar solo en el webhook).
5. Si `approved` → transición PENDIENTE→CONFIRMADO + decremento stock (UoW atómico).

**Estados MP → acción Food Store:**
- `approved` → avanza pedido a CONFIRMADO automáticamente.
- `pending` / `in_process` → pedido permanece en PENDIENTE.
- `rejected` → pedido en PENDIENTE, cliente puede reintentar.
- `cancelled` → cliente puede reintentar o cancelar pedido.

---

## Patrones aplicados

| Patrón | Capa | Descripción clave |
|--------|------|-------------------|
| Repository + BaseRepository[T] | Backend | Abstracción de acceso a BD. Facilita mocks. |
| Unit of Work | Backend | Transacciones atómicas. El Service nunca llama `session.commit()`. |
| Service Layer | Backend | Lógica de negocio stateless. Independiente del framework. |
| Snapshot | Backend/BD | `precio_snapshot` y `nombre_snapshot` en DetallePedido. `direccion_snapshot` en Pedido. Inmutables. |
| Soft Delete | Backend/BD | `deleted_at TIMESTAMPTZ`. NUNCA DELETE físico en entidades de negocio. |
| Audit Trail Append-Only | Backend/BD | `HistorialEstadoPedido`: solo INSERT. |
| FSM | Backend | Transiciones validadas en Service contra mapa de transiciones. |
| Idempotent Payments | Backend | `idempotency_key` UUID por pago. Webhook duplicado → ignorar. |
| Feature-Sliced Design | Frontend | Imports de arriba hacia abajo. Cada feature autocontenida. |
| Custom Hooks | Frontend | TanStack Query encapsulado en hooks por dominio. |
| Optimistic Updates | Frontend | Actualización inmediata de UI con rollback en error. |
| Webhook/IPN | Backend | MercadoPago notifica asíncronamente. Sin polling. |

---

## Seed data obligatorio

Ejecutar DESPUÉS de `alembic upgrade head`:

```bash
python -m app.db.seed
```

Carga: Roles (ADMIN/STOCK/PEDIDOS/CLIENT) · EstadoPedido (6 estados con es_terminal) · FormaPago (MERCADOPAGO/EFECTIVO/TRANSFERENCIA) · Usuario admin (`admin@foodstore.com` / `Admin1234!`).

El script es idempotente (ejecutarlo múltiples veces no duplica datos).

---

## Variables de entorno requeridas

Backend (`.env`):
```
DATABASE_URL=postgresql://user:pass@localhost:5432/foodstore_db
SECRET_KEY=<mínimo 32 chars aleatorios>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=["http://localhost:5173"]
MP_ACCESS_TOKEN=TEST-xxxx
MP_PUBLIC_KEY=TEST-xxxx
MP_NOTIFICATION_URL=https://dominio.com/api/v1/pagos/webhook
```

Frontend (`.env`):
```
VITE_API_URL=http://localhost:8000
VITE_MP_PUBLIC_KEY=TEST-xxxx
```

---

## Flujo de desarrollo OPSX

```
/opsx:explore   → pensar antes de comprometerse (opcional)
/opsx:propose   → generar propuesta + diseño + tareas
/opsx:apply     → implementar tarea por tarea
/opsx:archive   → sincronizar specs y cerrar el change
```

### Estado actual de los changes (ver CHANGES.md para detalle)

| # | Change | Estado |
|---|--------|--------|
| 1 | setup-backend | — |
| 2 | setup-frontend | — |
| 3 | auth-roles | — |
| 4 | categoria-crud | — |
| 5 | ingrediente-crud | — |
| 6 | producto-crud | — |
| 7 | cliente-crud | — |
| 8 | carrito-pedidos | — |
| 9 | pago-gestion | — |
| 10 | despacho-pedidos | — |
| 11 | administracion-general | — |
| 12 | frontend-ajustes-finales | — |
| 13 | pruebas-integracion | — |
| 14 | despliegue-entrega | — |

**Regla**: un change solo se puede comenzar si sus dependencias están ARCHIVADAS, no solo propuestas.

---

## Checklist de entrega (CE-01 a CE-14)

Antes de dar por terminado el proyecto verificar:
- CE-04: `alembic upgrade head` sin errores en BD limpia.
- CE-05: `python -m app.db.seed` carga datos iniciales.
- CE-10: ningún `service.session.commit()` directo (todo por UoW).
- CE-11: 4 stores Zustand implementados, tipados, con persist correcto.
- CE-13: video demostración (5-10 min) en README.

Rúbrica total: 200 puntos. Bonus: +10 pts tests (pytest, cobertura > 60%) · +10 pts deploy. Penalización: -30% si no corre localmente siguiendo el README.

---

## Convenciones de código

- Backend: `snake_case` para variables/funciones, `PascalCase` para clases.
- Frontend: `camelCase` para variables/funciones, `PascalCase` para componentes.
- Funciones < 50 líneas. SRP. Docstrings en Python. JSDoc en TypeScript.
- Commits: conventional commits (`feat(modulo):`, `fix(modulo):`, `refactor(modulo):`, etc.)
- `.env` NUNCA se commitea. Solo `.env.example`.
