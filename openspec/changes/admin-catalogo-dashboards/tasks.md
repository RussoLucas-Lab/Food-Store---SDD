## 1. Servicios API Admin

- [x] 1.1 Crear `frontend/src/features/admin/services/adminCategoriasApi.ts` con funciones: `getCategorias()`, `createCategoria(data)`, `updateCategoria(id, data)`, `deleteCategoria(id)` usando axios con header de autenticación
- [x] 1.2 Crear `frontend/src/features/admin/services/adminIngredientesApi.ts` con funciones: `getIngredientes()`, `createIngrediente(data)`, `updateIngrediente(id, data)`, `deleteIngrediente(id)`
- [x] 1.3 Crear `frontend/src/features/admin/services/adminProductosApi.ts` con funciones: `getProductos()`, `getProductoDetalle(id)`, `createProducto(data)`, `updateProducto(id, data)`, `deleteProducto(id)`
- [x] 1.4 Actualizar `frontend/src/features/admin/services/index.ts` para exportar los tres nuevos servicios

## 2. Hooks TanStack Query

- [x] 2.1 Crear `frontend/src/features/admin/hooks/useCategorias.ts` con: `useCategoriasQuery()` (useQuery para lista), `useCreateCategoria()`, `useUpdateCategoria()`, `useDeleteCategoria()` (useMutation con invalidateQueries)
- [x] 2.2 Crear `frontend/src/features/admin/hooks/useIngredientes.ts` con: `useIngredientesQuery()`, `useCreateIngrediente()`, `useUpdateIngrediente()`, `useDeleteIngrediente()`
- [x] 2.3 Crear `frontend/src/features/admin/hooks/useProductosAdmin.ts` con: `useProductosAdminQuery()`, `useCreateProducto()`, `useUpdateProducto()`, `useDeleteProducto()`
- [x] 2.4 Actualizar `frontend/src/features/admin/hooks/index.ts` para exportar los tres nuevos hooks

## 3. Página CategoriasAdminPage

- [x] 3.1 Crear `frontend/src/features/admin/pages/CategoriasAdminPage.tsx` con: tabla paginada (10 por página), columnas ID/Nombre/Descripción/Estado/Acciones, estado de loading y vacío
- [x] 3.2 Agregar botón "Nueva Categoría" que abre modal con formulario (campos: nombre requerido, descripción opcional)
- [x] 3.3 Implementar lógica de edición: botón por fila que abre el mismo modal pre-cargado con los datos de la categoría seleccionada
- [x] 3.4 Implementar lógica de eliminación: botón por fila que llama a `window.confirm()` con el nombre y luego ejecuta la mutación de delete
- [x] 3.5 Agregar toast de feedback (éxito/error) para crear, editar y eliminar
- [x] 3.6 Agregar validación en cliente: nombre requerido, máx 100 chars; descripción máx 500 chars
- [x] 3.7 Agregar paginación en cliente (slice del array, botones anterior/siguiente, indicador "Página X de Y")

## 4. Página IngredientesAdminPage

- [x] 4.1 Crear `frontend/src/features/admin/pages/IngredientesAdminPage.tsx` con: tabla paginada, columnas ID/Nombre/Unidad/Stock/Mínimo/Alerta/Estado/Acciones
- [x] 4.2 Mostrar badge de alerta de stock bajo (rojo) cuando `alerta_stock_bajo=true`
- [x] 4.3 Agregar botón "Nuevo Ingrediente" que abre modal con campos: nombre (req), unidad_medida (selector con 5 opciones), cantidad_stock (≥0, req), cantidad_minima (≥0, req), descripcion (opc), categoria_id (selector con categorías cargadas, opc)
- [x] 4.4 Implementar lógica de edición: modal pre-cargado solo con campos editables (nombre, descripcion, cantidad_stock, cantidad_minima — sin unidad_medida ni categoria_id)
- [x] 4.5 Implementar lógica de eliminación con `window.confirm()` y toast
- [x] 4.6 Agregar validación en cliente para cantidad_stock y cantidad_minima (≥0 requerido)
- [x] 4.7 Agregar paginación en cliente (misma lógica que CategoriasAdminPage)

## 5. Página ProductosAdminPage

- [x] 5.1 Crear `frontend/src/features/admin/pages/ProductosAdminPage.tsx` con: tabla paginada, columnas ID/Nombre/Precio/Stock disp./Estado/Acciones
- [x] 5.2 Mostrar badges de categorías (máx 2 visibles + "y N más") en la columna de categorías
- [x] 5.3 Agregar botón "Nuevo Producto" que abre modal con: nombre (req), base_price (>0, req), descripcion (opc), checkboxes de categorías (req mín 1, cargar con `useCategoriasQuery`), tabla dinámica de ingredientes con cantidad_requerida (req mín 1, cargar con `useIngredientesQuery`)
- [x] 5.4 Implementar tabla dinámica de ingredientes en el modal: selector de ingrediente + campo numérico de cantidad + botón para eliminar la fila + botón "Agregar ingrediente"
- [x] 5.5 Implementar lógica de edición: `useProductoDetalle(id)` para obtener categorías e ingredientes actuales y pre-cargar el modal
- [x] 5.6 Implementar lógica de eliminación con `window.confirm()` y toast
- [x] 5.7 Agregar validación en cliente: nombre req, base_price >0, al menos 1 categoría seleccionada, al menos 1 ingrediente con quantity_required >0
- [x] 5.8 Agregar paginación en cliente

## 6. Router y Navegación

- [x] 6.1 Actualizar `frontend/src/router.tsx`: agregar rutas `/admin/categorias`, `/admin/ingredientes`, `/admin/productos` dentro del bloque de ProtectedRoute de admin
- [x] 6.2 Agregar redirect de ruta obsoleta: `<Route path="catalogo" element={<Navigate to="/admin/categorias" replace />} />`
- [x] 6.3 Actualizar `frontend/src/features/admin/components/AdminNav.tsx`: reemplazar el item "Catálogo" por tres items separados — "Categorías" (`/admin/categorias`), "Ingredientes" (`/admin/ingredientes`), "Productos" (`/admin/productos`) — todos visibles para ADMIN y STOCK

## 7. Barrel Exports y Limpieza

- [x] 7.1 Actualizar `frontend/src/features/admin/pages/index.ts` para exportar las tres nuevas páginas y remover `CatalogoAdminPage`
- [x] 7.2 Eliminar el archivo `frontend/src/features/admin/pages/CatalogoAdminPage.tsx`
- [x] 7.3 Verificar que no quedan imports de `CatalogoAdminPage` en ningún archivo (router ya actualizado en tarea 6.1)
