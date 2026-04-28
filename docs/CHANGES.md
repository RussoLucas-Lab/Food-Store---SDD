# Mapa de Changes — Food Store SDD / OPSX

Este documento reemplaza la guía genérica de changes. Es el plan detallado y secuencial de changes atómicos para desarrollar TODO el proyecto Food Store, siguiendo SDD (Spec-Driven Development) y OPSX. Cada change describe el QUÉ, las historias de usuario, y las dependencias técnicas y funcionales.

---

## Tabla Resumida — Changes planificados

| Change (kebab-case)         | Funcionalidad                             | Historias cubiertas                        | Depende de                 |
|----------------------------|-------------------------------------------|---------------------------------------------|----------------------------|
| setup-backend              | Estructura base backend (configs, repo, UoW, models seed) | — (infraestructura base)             | —                          |
| setup-frontend             | Estructura base frontend (vite, rutas, layout, slices)    | — (infraestructura base)             | —                          |
| auth-roles                 | Registro, login, control de acceso, roles, sesiones       | HU1, HU2, HU3, HU4, HU20                 | setup-backend, setup-frontend    |
| categoria-crud             | CRUD de categorías, validaciones, casos borde             | HU5, HU23, HU25                        | auth-roles                 |
| ingrediente-crud           | CRUD de ingredientes con lógica de stock                  | HU6, HU22, HU26                        | categoria-crud                 |
| producto-crud              | CRUD de productos (alta, baja, modif., stock), link ingredientes y categorías | HU7, HU8, HU9, HU26            | ingrediente-crud            |
| cliente-crud               | Registro, edición, borrado de clientes, validaciones      | HU10, HU27                            | auth-roles                 |
| carrito-pedidos            | ABM de carrito, creación de pedido                          | HU11, HU12, HU13, HU14                 | producto-crud, cliente-crud     |
| pago-gestion               | Integración y lógica de pagos (alta, cobro, anulaciones)  | HU15, HU16, HU17                       | carrito-pedidos             |
| despacho-pedidos           | Gestión y seguimiento de despacho/entrega de pedidos      | HU18, HU21, HU28                        | pago-gestion                 |
| administracion-general     | Panel admin, métricas, reportes, parámetros generales     | HU19, HU24                            | Todos los anteriores        |
| frontend-ajustes-finales   | Errores, UX, validaciones, mobile, testing UI             | HUall                                 | Todos los anteriores        |
| pruebas-integracion        | Pruebas e2e: flujo completo usuario a pago/despacho       | Flujo transversal                      | Todos los anteriores        |
| despliegue-entrega         | Scripts de deploy, build final, migraciones, documentación| —                                     | Todos los anteriores        |

---

## Change 1: setup-backend
**Funcionalidad:** Estructura inicial backend, patron Repository+UoW, modelos base, seeds de entorno y config mínima.
**Historias:** Infraestructura, nada funcional directo.
**Depende de:** —

## Change 2: setup-frontend
**Funcionalidad:** Base del frontend, Vite, estructura de carpetas por feature-slice, layout principal, rutas vacías.
**Historias:** Infraestructura, sin lógica aún.
**Depende de:** —

## Change 3: auth-roles
**Funcionalidad:** Registro, login, control de acceso, definición y verificación de roles, sesiones seguras.
**Historias:** HU1 (Login), HU2 (Registro), HU3 (Roles), HU4 (Logout), HU20 (Validaciones de usuario)
**Depende de:** setup-backend, setup-frontend

## Change 4: categoria-crud
**Funcionalidad:** Alta/baja/modificación/listado de categorías, validaciones estrictas, sin cross-feature aún.
**Historias:** HU5, HU23, HU25 (categorías, restricciones de uso, manejo de estados)
**Depende de:** auth-roles

## Change 5: ingrediente-crud
**Funcionalidad:** CRUD de ingredientes, lógica de stock, aislamiento por roles.
**Historias:** HU6, HU22, HU26
**Depende de:** categoria-crud

## Change 6: producto-crud
**Funcionalidad:** ABM de productos, precios, stock, relación ingredientes-categoría, business rules.
**Historias:** HU7, HU8, HU9, HU26
**Depende de:** ingrediente-crud

## Change 7: cliente-crud
**Funcionalidad:** Registro/edición baja clientes, validaciones contexto, posible integración identidad.
**Historias:** HU10, HU27
**Depende de:** auth-roles

## Change 8: carrito-pedidos
**Funcionalidad:** Carrito editable y creación de pedidos, validaciones, precios y cálculo stock, asociación con productos y cliente actual.
**Historias:** HU11, HU12, HU13, HU14
**Depende de:** producto-crud, cliente-crud

## Change 9: pago-gestion
**Funcionalidad:** Integración pago, validación pagos, rollback, confirmaciones y anulaciones.
**Historias:** HU15, HU16, HU17
**Depende de:** carrito-pedidos

## Change 10: despacho-pedidos
**Funcionalidad:** Gestión de estados de despacho para pedidos, tracking, avisos, reglas de consistencia.
**Historias:** HU18, HU21, HU28
**Depende de:** pago-gestion

## Change 11: administracion-general
**Funcionalidad:** Pantalla/config admin, inyección de métricas, parámetros globales, reportes integrados.
**Historias:** HU19, HU24
**Depende de:** Todos los anteriores

## Change 12: frontend-ajustes-finales
**Funcionalidad:** Validaciones de UI, feedback, palabras reservadas, UX móvil y desktop, pruebas de usuario.
**Historias:** HUall
**Depende de:** Todos los anteriores

## Change 13: pruebas-integracion
**Funcionalidad:** Test e2e, validación de flujos críticos: compra, pago, despacho, error paths.
**Historias:** Flujo transversal
**Depende de:** Todos los anteriores

## Change 14: despliegue-entrega
**Funcionalidad:** Build final, scripts de entrega, documentación deploy, exportación specs finales.
**Historias:** —
**Depende de:** Todos los anteriores

---

## Notas clave y buenas prácticas:
- No saltear dependencias: un change depende de estar ARCHIVADO, no sólo propuesto.
- Intenta mantener cada change de tamaño razonable/tareas atómicas (evitar phases gigantes).
- Este listado es punto de partida: puede ampliarse si se detectan casos especiales o bugs fuera del plan.
- Actualizá este archivo sólo junto con el equipo, usando la historia y specs TRAZABLES (no perder contexto ni la motivación de cada change).

---

¿Dudas? ¿Detectás un caso sin cubrir? Usá `/opsx:explore` antes de proponer el siguiente change.
Esta hoja de ruta es el núcleo operativo para Food Store usando OPSX/SDD.