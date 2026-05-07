## 1. Database & Migrations

- [x] 1.1 Crear migration: tabla `products` (id, name, description, base_price, status, created_at, updated_at)
- [x] 1.2 Crear migration: tabla `product_categories` (product_id, category_id) - composite PK + FKs
- [x] 1.3 Crear migration: tabla `product_ingredients` (id, product_id, ingredient_id, quantity_required) - FKs + unique(product_id, ingredient_id)
- [x] 1.4 Crear índices: product_categories(category_id), product_ingredients(product_id, ingredient_id)
- [x] 1.5 Ejecutar y verificar migrations

## 2. Backend Models & Repositories

- [x] 2.1 Crear modelo `Product` en `backend/models/product.py` con atributos: id, name, description, base_price, status, created_at, updated_at
- [x] 2.2 Crear modelo `ProductIngredient` en `backend/models/product_ingredient.py` con atributos: id, product_id, ingredient_id, quantity_required
- [x] 2.3 Crear clase `ProductRepository` en `backend/repositories/product_repository.py` con métodos: 
  - `create(name, description, base_price, categories, ingredients)`
  - `get_by_id(product_id)`
  - `list_all(status='active', category_id=None, search=None, skip=0, limit=50)`
  - `update(product_id, name, description, base_price, categories, ingredients)`
  - `delete(product_id)` (soft delete si existe en pedidos, hard delete si no)
  - `get_products_by_category(category_id)`
  - `get_products_using_ingredient(ingredient_id)`
  - `is_product_used_in_orders(product_id)` (verificar si existe en tabla orders)
- [x] 2.4 Crear clase `ProductIngredientRepository` en `backend/repositories/product_ingredient_repository.py` con métodos:
  - `create(product_id, ingredient_id, quantity_required)`
  - `get_by_product(product_id)`
  - `delete_by_product(product_id)`
  - `get_ingredient_usage_in_products(ingredient_id)`
- [x] 2.5 Integrar ProductRepository en UnitOfWork (backend/uow/uow.py)

## 3. Backend Validation & Business Logic Service

- [x] 3.1 Crear clase `ProductService` en `backend/services/product_service.py` con métodos:
   - `validate_product_input(name, description, base_price, categories, ingredients)` - validar campos, uniqueness de name
  - `validate_categories_exist(category_ids)` - verificar que todas las categorías existan
  - `validate_ingredients_exist(ingredients)` - verificar que todos los ingredientes existan y quantity_required > 0
  - `calculate_product_stock(product_id)` - calcular min(stock_disponible_ingrediente / quantity_required)
  - `check_can_delete_category(category_id)` - verificar si hay productos activos
  - `check_can_delete_ingredient(ingredient_id)` - verificar si hay productos activos
  - `check_can_modify_product(product_id)` - verificar si está en pedidos
- [x] 3.2 Crear validadores de request en `backend/schemas/product_schemas.py`:
  - `ProductCreateRequest` con validaciones de name (required, unique), description (max 500), base_price (> 0), categories (array min 1), ingredients (array min 1)
  - `ProductUpdateRequest` análogo
  - `ProductResponse`, `ProductDetailResponse` (incluir stock calculado)

## 4. Backend API Endpoints

- [x] 4.1 Crear blueprint/router en `backend/routes/products.py`:
  - `POST /api/productos` - crear producto
  - `GET /api/productos` - listar con filtros (category, search, status)
  - `GET /api/productos/:id` - detalle
  - `GET /api/productos/:id/stock` - stock disponible calculado
  - `PUT /api/productos/:id` - actualizar
  - `DELETE /api/productos/:id` - desactivar/eliminar
- [x] 4.2 Implementar request/response handling, error codes (400, 404, 409)
- [x] 4.3 Integrar autenticación/autorización según cambio auth-roles (verificar permisos de admin para editar)
- [x] 4.4 Registrar blueprint en aplicación principal

## 5. Backend Integrity & Hooks

- [x] 5.1 Modificar `CategoryRepository.delete()` para validar `check_can_delete_category()` - retornar 409 si hay productos
- [x] 5.2 Modificar `IngredientRepository.delete()` para validar `check_can_delete_ingredient()` - retornar 409 si hay productos
- [x] 5.3 Asegurar que al actualizar stock de ingrediente, los productos que lo usan reflejen el cambio (ya sucede automático si el cálculo es en tiempo de lectura)
- [x] 5.4 Documentar en README backend los cambios a CategoryRepository e IngredientRepository

## 6. Backend Tests

**STATUS: DEFERRED** → See change: `backend-tests-fix` (to be created)

Tests will be unified with CategoryService + IngredientService tests for consistency.

- [ ] 6.1 Test unitarios: `test_product_service.py` - validaciones, cálculo de stock
  - Test: crear producto válido
  - Test: crear con price <= 0
  - Test: crear sin categoría
  - Test: nombre duplicado
  - Test: cálculo de stock con múltiples ingredientes
- [ ] 6.2 Test de integración: `test_product_endpoints.py`
  - Test POST /api/products exitoso
  - Test POST /api/products con validaciones fallidas (400)
  - Test GET /api/products/:id no existe (404)
  - Test GET /api/products con filtros
  - Test GET /api/products/:id/stock calculado correctamente
  - Test PUT /api/products/:id actualización exitosa
  - Test PUT /api/products/:id en producto en pedidos (403)
  - Test DELETE /api/products/:id soft/hard delete
  - Test DELETE /api/categories/:id si está en uso (409)
  - Test DELETE /api/ingredients/:id si está en uso (409)
- [ ] 6.3 Ejecutar tests, verificar coverage > 80%

## 7. Frontend Pages & Components

**STATUS: DEFERRED** → See change: `producto-frontend-crud` (to be created)

- [ ] 7.1 Crear página `ProductListPage` en `frontend/pages/products/list/` - tabla con productos activos, filtros por categoría/nombre, botones crear/editar/ver
- [ ] 7.2 Crear página `ProductDetailPage` en `frontend/pages/products/detail/` - muestra detalles, composición, stock calculado, botones editar/desactivar
- [ ] 7.3 Crear página `ProductFormPage` en `frontend/pages/products/form/` - formulario para crear/editar producto
- [ ] 7.4 Crear componente `CategorySelector` - dropdown/multi-select para elegir categorías
- [ ] 7.5 Crear componente `IngredientCompositionEditor` - tabla editable con ingredientes + cantidades, botón agregar/quitar
- [ ] 7.6 Crear componente `ProductCard` - card display para listados (nombre, categorías, stock, precio)

## 8. Frontend API Integration

**STATUS: DEFERRED** → See change: `producto-frontend-crud`

- [ ] 8.1 Crear `ProductAPI` en `frontend/services/product-api.ts` con funciones:
   - `createProduct(data)`
   - `getProduct(id)`
   - `listProducts(filters)`
   - `updateProduct(id, data)`
   - `deleteProduct(id)`
   - `getProductStock(id)`
- [ ] 8.2 Crear `hooks/useProducts.ts` - custom hook para manejo de estado/queries
- [ ] 8.3 Integrar con dropdowns de categorías e ingredientes (llamadas GET a endpoints correspondientes)
- [ ] 8.4 Manejo de estados de carga, errores, validaciones de formulario

## 9. Frontend Routing & Navigation

**STATUS: DEFERRED** → See change: `producto-frontend-crud`

- [ ] 9.1 Agregar rutas a `frontend/router/index.ts` (o equivalente):
   - `/products` → ProductListPage
   - `/products/:id` → ProductDetailPage
   - `/products/new` → ProductFormPage (create)
   - `/products/:id/edit` → ProductFormPage (edit)
- [ ] 9.2 Agregar links en menú de navegación principal
- [ ] 9.3 Verificar permisos: solo admin puede crear/editar/eliminar

## 10. Frontend Tests

**STATUS: DEFERRED** → See change: `producto-frontend-crud`

- [ ] 10.1 Test unitarios de componentes: CategorySelector, IngredientCompositionEditor, ProductCard
- [ ] 10.2 Test de integración: ProductListPage, ProductDetailPage, ProductFormPage
   - Test: listar productos
   - Test: crear producto exitoso
   - Test: editar producto
   - Test: eliminar producto
   - Test: filtrar por categoría
   - Test: validaciones de formulario
- [ ] 10.3 Test de mock API responses

## 11. Documentation & Handoff

**STATUS: PARTIAL** → Backend docs done, frontend pending

- [x] 11.1 Documentar endpoints en README o Swagger/OpenAPI spec
   - POST /api/productos
   - GET /api/productos
   - GET /api/productos/:id
   - GET /api/productos/:id/stock
   - PUT /api/productos/:id
   - DELETE /api/productos/:id
- [x] 11.2 Documentar cambios a endpoints de categoría e ingrediente (nuevas validaciones)
- [x] 11.3 Verificar que specs en openspec/specs/product-crud/spec.md se cumplen completamente
- [ ] 11.4 Crear CHANGELOG entry en CHANGELOG.md o docs/CHANGES.md
- [ ] 11.5 Revisar con equipo: diseño, implementación, tests

## 12. Integration Testing & Verification

**STATUS: DEFERRED** → Backend implementation complete, E2E tests in backend-tests-fix change

- [ ] 12.1 Test end-to-end manual: crear producto con categorías e ingredientes
- [ ] 12.2 Verificar stock se calcula correctamente al cambiar ingrediente stock
- [ ] 12.3 Verificar que no se puede eliminar categoría/ingrediente si está en uso
- [ ] 12.4 Verificar que no se puede modificar producto si está en pedido
- [ ] 12.5 Verificar que listados filtran correctamente por categoría, nombre
- [ ] 12.6 Smoke tests con datos de ejemplo en dev/test

## 13. Archive & Ready for Next Change

**STATUS: READY TO ARCHIVE BACKEND**

- [x] 13.1 Backend: Toda funcionalidad está implementada (CRUD + validaciones + integridad referencial)
- [ ] 13.2 Ejecutar archivado: `openspec archive --change "producto-crud"`
- [ ] 13.3 Verificar que specs se sincronizaron a openspec/specs/
- [ ] 13.4 Commit git con mensaje convencional: "feat(product): add CRUD and stock calculation (backend only)"
- [ ] 13.5 Frontend y tests → nuevos changes: `producto-frontend-crud` y `backend-tests-fix`
