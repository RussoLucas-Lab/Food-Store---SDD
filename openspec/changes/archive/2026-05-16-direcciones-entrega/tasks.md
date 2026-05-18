## 1. Modelo y módulo

- [x] 1.1 Crear el directorio `backend/modules/direcciones/` con `__init__.py`
- [x] 1.2 Crear `model.py` con la clase `DireccionEntrega` (campos: `id`, `cliente_id`, `calle`, `numero`, `ciudad`, `provincia`, `codigo_postal`, `piso`, `departamento`, `referencia`, `es_predeterminada`, `activo`, `created_at`, `updated_at`)
- [x] 1.3 Implementar `__repr__` y `to_dict()` en `DireccionEntrega` siguiendo el patrón de `Cliente`

## 2. Repositorio

- [x] 2.1 Crear `repository.py` con la interfaz abstracta `IDireccionRepository` (ABC)
- [x] 2.2 Implementar `InMemoryDireccionRepository` con `dict[int, DireccionEntrega]` y `_next_id`
- [x] 2.3 Implementar `create(cliente_id, **campos)` que asigna id autoincremental
- [x] 2.4 Implementar `get_by_id(direccion_id)` que devuelve solo direcciones activas
- [x] 2.5 Implementar `list_by_cliente(cliente_id)` filtrando solo activas
- [x] 2.6 Implementar `update(direccion_id, **campos)` y `soft_delete(direccion_id)`
- [x] 2.7 Implementar `count_by_cliente(cliente_id)` para soportar RN-DI01
- [x] 2.8 Implementar `set_predeterminada(direccion_id)` que desmarca el resto de direcciones del mismo cliente (invariante RN-DI02)

## 3. Schemas y excepciones

- [x] 3.1 Crear `schemas.py` con `DireccionCreate` (obligatorios + opcionales + `es_predeterminada: bool = False`, sin `cliente_id`)
- [x] 3.2 Agregar `DireccionUpdate` con todos los campos opcionales para edición parcial
- [x] 3.3 Agregar `DireccionResponse` con `id`, `cliente_id`, `es_predeterminada`, `activo`, timestamps
- [x] 3.4 Crear `exceptions.py` con `DireccionNotFound` y `UnauthorizedDireccionAccess`

## 4. Servicio

- [x] 4.1 Crear `service.py` con `DireccionService` que recibe el UoW en el constructor
- [x] 4.2 Implementar `create_direccion(user_id, dto)` con RN-DI01 (primera dirección → `es_predeterminada=True` forzado)
- [x] 4.3 Aplicar RN-DI02 en `create_direccion`: si `es_predeterminada=True`, desmarcar las demás del cliente
- [x] 4.4 Implementar `list_direcciones(user_id)` devolviendo solo las del cliente
- [x] 4.5 Implementar `update_direccion(user_id, direccion_id, dto)` con verificación de ownership (RN-DI03)
- [x] 4.6 Implementar `set_predeterminada(user_id, direccion_id)` con ownership + unicidad (RN-DI02)
- [x] 4.7 Implementar `delete_direccion(user_id, direccion_id)` con soft delete y reasignación de predeterminada si corresponde
- [x] 4.8 Asegurar que el servicio lanza `DireccionNotFound` (404) y `UnauthorizedDireccionAccess` (403) y nunca llama `commit()` directo

## 5. Router REST

- [x] 5.1 Crear `router.py` con prefijo `/clientes/me/direcciones`, instanciando UoW y Service a nivel de módulo
- [x] 5.2 Implementar `POST /clientes/me/direcciones` con `require_role("client", "admin")` → HTTP 201
- [x] 5.3 Implementar `GET /clientes/me/direcciones` → HTTP 200 con lista propia
- [x] 5.4 Implementar `PUT /clientes/me/direcciones/{id}` → HTTP 200
- [x] 5.5 Implementar `DELETE /clientes/me/direcciones/{id}` → HTTP 204
- [x] 5.6 Implementar `PUT /clientes/me/direcciones/{id}/predeterminada` → HTTP 200
- [x] 5.7 Mapear excepciones a HTTP: `DireccionNotFound`→404, `UnauthorizedDireccionAccess`→403, `ValueError`→400

## 6. Integración con UoW y app

- [x] 6.1 Agregar la propiedad abstracta `direcciones` en `IUnitOfWork` (`backend/core/uow.py`)
- [x] 6.2 Instanciar `InMemoryDireccionRepository` y exponer la propiedad `direcciones` en `InMemoryUnitOfWork` (`backend/core/uow_inmemory.py`)
- [x] 6.3 Registrar el router de direcciones en `backend/main.py`
- [x] 6.4 Verificar que `carrito-pedidos` resuelve `uow.direcciones.get_by_id()` sin errores

## 7. Tests backend

- [x] 7.1 Crear `backend/tests/modules/direcciones/__init__.py`
- [x] 7.2 Tests de `DireccionService`: primera dirección es predeterminada (RN-DI01)
- [x] 7.3 Tests de `DireccionService`: solo una predeterminada a la vez (RN-DI02)
- [x] 7.4 Tests de `DireccionService`: ownership rechaza acceso a dirección ajena (RN-DI03)
- [x] 7.5 Tests de `DireccionService`: reasignación de predeterminada al eliminar
- [x] 7.6 Tests de endpoints: CRUD completo + códigos HTTP (201, 200, 204, 403, 404, 401)

## 8. Frontend

- [x] 8.1 Crear `frontend/src/features/pedidos/services/direccionClient.ts` con llamadas a `/api/v1/clientes/me/direcciones`
- [x] 8.2 Conectar `DirectionSelector.tsx` a la API real con TanStack Query (listado de direcciones)
- [x] 8.3 Exponer la dirección seleccionada para el `CartCreateDTO` del checkout
- [x] 8.4 Crear componente `DireccionManager` con UI CRUD (alta, edición, baja, marcar predeterminada)
- [x] 8.5 Verificar que el estado de servidor vive en TanStack Query y no en Zustand
