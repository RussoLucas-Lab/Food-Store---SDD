## Why

Hasta ahora el sistema tiene catálogo, pedidos, pagos y despacho operativos, pero
no existe un panel centralizado de administración. El ADMIN no puede gestionar
usuarios ni ver métricas del negocio, y el STOCK no tiene una interfaz unificada
para administrar catálogo e inventario. Este change consolida la capa de gestión:
dashboard de métricas, administración de usuarios y un panel de catálogo/stock,
cerrando las épicas 15, 16 y 17 del proyecto.

## What Changes

- **Backend — Métricas (NUEVO)**: módulo `admin` con endpoints de agregación
  (`SUM`, `COUNT`, `GROUP BY`, `DATE_TRUNC`) para resumen general, ventas por
  período, top productos vendidos y distribución de pedidos por estado. Solo rol ADMIN.
- **Backend — Gestión de usuarios (NUEVO)**: endpoints para listar usuarios con
  búsqueda/filtro/paginación, editar datos y roles, y activar/desactivar cuentas.
  Solo rol ADMIN. Al cambiar rol o desactivar se invalidan los refresh tokens del
  usuario afectado para forzar re-login con permisos actualizados.
- **Backend — Validación de cuenta activa**: el login rechaza con HTTP 403 a
  usuarios con `activo=false`.
- **Backend — RBAC ampliado en catálogo y pedidos**: los endpoints de gestión de
  catálogo aceptan `ADMIN` además de `STOCK`; los de gestión de pedidos aceptan
  `ADMIN` además de `PEDIDOS` (US-064, US-065).
- **Frontend — Panel de administración (NUEVO)**: layout del admin con navegación
  por rol; dashboard con métricas y gráficos recharts (líneas, barras, torta);
  pantalla de gestión de usuarios; pantallas de gestión de catálogo (categorías,
  ingredientes, productos) y de stock con alertas de bajo stock; integración de la
  vista de despacho de pedidos ya existente.

## Capabilities

### New Capabilities
- `admin-metricas`: endpoints backend de agregación de métricas (resumen, ventas
  por período, top productos, pedidos por estado) restringidos a rol ADMIN.
- `admin-usuarios`: endpoints backend de gestión de usuarios — listado con
  búsqueda/filtro/paginación, edición de datos y roles, activación/desactivación,
  e invalidación de refresh tokens al modificar acceso.
- `admin-panel-frontend`: panel de administración en el frontend — layout con
  navegación por rol, dashboard de métricas con gráficos recharts, pantalla de
  gestión de usuarios, y panel de gestión de catálogo y stock con alertas.

### Modified Capabilities
<!-- Ninguna. La validación de cuenta activa en el login es comportamiento nuevo
     y se especifica como requisito ADDED dentro de `admin-usuarios`, ya que la
     spec `autenticacion` existente no contiene un requisito de login que modificar. -->


## Impact

- **Backend**: nuevo módulo `backend/modules/admin/` (router, service, repository,
  schemas) siguiendo Router → Service → UoW → Repository. Modificación del módulo
  `clientes`/`usuarios` para los endpoints de gestión y del campo `activo` en el
  modelo `Usuario`. Ajuste de dependencias de rol (`require_roles`) en routers de
  catálogo y pedidos. Modificación del flujo de login en `auth`.
- **Frontend**: nueva feature `admin/` completa (pages, components, hooks,
  services) hoy solo presente como stubs vacíos. Uso de `recharts` para gráficos
  y TanStack Query para el estado de servidor de métricas y usuarios.
- **API**: nuevos endpoints bajo `/api/v1/admin/*` (métricas y usuarios).
- **Dependencias**: `recharts` ya está previsto en el stack del frontend.
- **Fuera de alcance**: el panel de configuración del sistema (US-060, prioridad
  Baja) no se incluye en este change.
