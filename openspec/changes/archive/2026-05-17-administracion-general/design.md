## Context

El backend ya expone catálogo, pedidos, pagos y despacho. El frontend tiene la
tienda, el carrito, el checkout y la vista de despacho. Falta la capa de gestión:
un panel de administración para ADMIN y STOCK.

Estado actual relevante:
- `backend/modules/` contiene `auth`, `categorias`, `clientes`, `direcciones`,
  `ingredientes`, `pagos`, `pedidos`, `productos`. **No existe** `modules/admin/`.
- El modelo de usuario vive en `backend/modules/clientes/model.py` (la entidad
  `Usuario`); la gestión de roles RBAC ya está implementada (auth-roles archivado).
- `frontend/src/features/admin/` existe solo como stubs vacíos (`index.ts` en
  `components/`, `hooks/`, `pages/`, `services/`).
- El despacho de pedidos ya tiene UI propia (`pedido-despacho-frontend`).

Restricciones del proyecto: arquitectura backend Router → Service → UoW →
Repository; el Service nunca hace `session.commit()`. Frontend Feature-Sliced
Design; Zustand para estado de cliente, TanStack Query para estado de servidor.
Errores RFC 7807. Paginación `?page&size`.

## Goals / Non-Goals

**Goals:**
- Exponer endpoints de métricas agregadas para el dashboard del ADMIN.
- Exponer endpoints de gestión de usuarios (listado, edición de roles,
  activación/desactivación) con invalidación de tokens al cambiar acceso.
- Ampliar el RBAC de catálogo (ADMIN+STOCK) y pedidos (ADMIN+PEDIDOS).
- Construir el panel de administración del frontend con dashboard, gestión de
  usuarios y gestión de catálogo/stock.
- Validar cuenta activa en el login.

**Non-Goals:**
- Panel de configuración del sistema (US-060, prioridad Baja) — fuera de alcance.
- Reescribir el CRUD de catálogo/pedidos — ya existe; solo se ajustan los guards
  de rol y se construye la UI de gestión que los consume.
- Reescribir la vista de despacho — se integra la pantalla ya existente.
- Métricas en tiempo real o caché — las queries se ejecutan on-demand por request.

## Decisions

### D1 — Nuevo módulo `backend/modules/admin/` para métricas
El dominio de métricas no pertenece a ningún módulo existente porque cruza
pedidos, productos y usuarios. Se crea `modules/admin/` con `router.py`,
`service.py`, `repository.py`, `schemas.py`. El repositorio de admin ejecuta
queries de agregación de solo lectura (`SUM`, `COUNT`, `GROUP BY`, `DATE_TRUNC`)
sobre las tablas de pedidos y detalle de pedido.
*Alternativa descartada*: dispersar las métricas en cada módulo de dominio —
generaría dependencias cruzadas y duplicación de lógica de agregación.

### D2 — Gestión de usuarios dentro de `modules/admin/` (router) reutilizando el repo de `clientes`
Los endpoints `/api/v1/admin/usuarios` se exponen desde el router de admin, pero
la persistencia de `Usuario` y `UsuarioRol` se hace a través del repositorio
existente del módulo `clientes` (vía UoW). Así se evita duplicar acceso a la
tabla `Usuario`. El `AdminUsuariosService` orquesta: leer/escribir usuario, leer
catálogo de roles, y revocar refresh tokens.
*Alternativa descartada*: crear un nuevo repositorio de usuarios en `admin/` —
duplicaría el acceso a una tabla ya gestionada por `clientes`.

### D3 — Invalidación de tokens al cambiar rol o desactivar
Cuando el ADMIN cambia el rol de un usuario o lo desactiva, todos los refresh
tokens de ese usuario se revocan dentro de la misma transacción UoW. El access
token vigente expira solo (≤ 30 min); no se mantiene blacklist de access tokens.
Esto cumple US-054/US-055 sin infraestructura adicional de revocación.
*Trade-off*: hay una ventana de hasta 30 min en la que el access token viejo
sigue válido — aceptable para el alcance académico.

### D4 — Endpoints de métricas separados por gráfico
Cuatro endpoints en lugar de uno monolítico:
- `GET /api/v1/admin/metricas/resumen` — KPIs (ventas totales, # pedidos,
  # usuarios, # productos sin stock).
- `GET /api/v1/admin/metricas/ventas?desde&hasta&granularidad` — serie temporal
  (LineChart). Granularidad dia/semana/mes vía `DATE_TRUNC`.
- `GET /api/v1/admin/metricas/productos-top?top&desde&hasta` — ranking (BarChart).
- `GET /api/v1/admin/metricas/pedidos-por-estado?desde&hasta` — distribución
  (PieChart).
Cada gráfico carga su propio query con su filtro de fecha; un endpoint por
visualización mantiene los queries simples y permite carga independiente en el
frontend.

### D5 — RBAC ampliado mediante la dependencia de roles existente
La protección por rol ya existe (auth-roles). Se reutiliza el helper
`require_roles(...)` aceptando múltiples roles: catálogo pasa a
`require_roles("ADMIN", "STOCK")`, pedidos a `require_roles("ADMIN", "PEDIDOS")`,
y los endpoints de admin a `require_roles("ADMIN")`.
No se crea infraestructura nueva de autorización.

### D6 — Métricas como ingresos de pedidos en estado de venta efectiva
"Ventas" se calcula sobre pedidos en estados que representan venta confirmada
(CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO), no sobre PENDIENTE ni CANCELADO. El
monto usa el `total` snapshot del pedido. El top de productos agrega
`DetallePedido.cantidad` y `precio_snapshot` de esos mismos pedidos.
*Alternativa descartada*: contar solo ENTREGADO — subestimaría el negocio activo.

### D7 — Feature `admin/` del frontend con sub-secciones por rol
Estructura FSD:
```
features/admin/
├── pages/        AdminLayout, DashboardPage, UsuariosPage,
│                 CatalogoAdminPage, StockPage
├── components/   KpiCard, VentasLineChart, TopProductosBarChart,
│                 PedidosEstadoPieChart, UsuarioRow, UsuarioRolEditor,
│                 StockAlertList, AdminNav
├── hooks/        useMetricasResumen, useMetricasVentas,
│                 useMetricasProductosTop, useMetricasPedidosEstado,
│                 useUsuarios, useUpdateUsuario, useToggleUsuarioActivo
└── services/     adminMetricasApi, adminUsuariosApi
```
El `AdminLayout` muestra navegación filtrada por rol del usuario autenticado
(STOCK ve solo Catálogo/Stock; PEDIDOS ve solo Despacho; ADMIN ve todo). Las
rutas se protegen con el guard de rutas por rol ya existente. Las pantallas de
gestión de catálogo consumen los endpoints CRUD de catálogo ya implementados.

### D8 — Estado de servidor con TanStack Query, sin nuevo store Zustand
Métricas y usuarios son estado de servidor → TanStack Query con hooks por
dominio. No se agrega un store Zustand: el proyecto fija exactamente 4 stores
(auth, cart, payment, ui) y mezclar estado de servidor en Zustand es un error
arquitectónico declarado en CLAUDE.md. Las mutaciones de usuario invalidan las
queries de listado para refrescar la UI.

### D9 — Alertas de bajo stock calculadas en el frontend sobre el catálogo
La pantalla de Stock reutiliza el endpoint de listado de productos (incluyendo
no disponibles) y marca como "bajo stock" los productos con `stock` por debajo
de un umbral configurable en el cliente (default 5). La actualización de stock
usa el endpoint `PATCH /api/v1/productos/{id}/stock` ya existente.
*Alternativa descartada*: un endpoint dedicado de alertas en backend — innecesario
para el alcance; el listado de productos ya trae el dato de stock.

## Risks / Trade-offs

- **Queries de agregación lentas con volumen alto** → para el alcance académico el
  volumen es bajo; las queries usan índices existentes sobre `creado_en` y FKs.
  Si hiciera falta, se añadirían índices o materialización en un change posterior.
- **Ventana de 30 min con access token viejo tras cambio de rol** (D3) → aceptado;
  el refresh token sí queda revocado de inmediato, forzando re-login al expirar.
- **El ADMIN podría degradar al último ADMIN** → mitigado: el service valida
  RN-RB04 y rechaza la operación si dejaría al sistema sin administradores.
- **El ADMIN podría desactivarse a sí mismo** → mitigado: el service rechaza la
  auto-desactivación del propio usuario autenticado.
- **Campo `activo` puede no existir aún en `Usuario`** → si falta, se agrega vía
  migración Alembic con default `true`; el login valida el flag.
- **Stubs vacíos en `features/admin/`** → se reemplazan por la implementación real;
  riesgo bajo, no hay código que romper.

## Migration Plan

1. Agregar campo `activo` (boolean, default `true`, not null) a `Usuario` si no
   existe — migración Alembic.
2. Crear `backend/modules/admin/` (router, service, repository, schemas) y
   registrarlo en `main.py` bajo `/api/v1/admin`.
3. Ajustar `require_roles` en routers de catálogo y pedidos.
4. Añadir validación de cuenta activa en el flujo de login de `auth`.
5. Implementar la feature `admin/` del frontend y registrar sus rutas en el router.
6. Rollback: revertir la migración de `activo`, quitar el registro del router de
   admin y los ajustes de `require_roles`; la feature de frontend es aditiva.

## Open Questions

- ¿El umbral de "bajo stock" debe ser global configurable en backend o basta con
  el default del cliente? — Se asume default de cliente (5) para este change.
- ¿Las métricas de ventas usan el `total` del pedido o `total - costo_envio`? — Se
  asume `total` (ingreso bruto del pedido); revisable si la rúbrica lo exige.
