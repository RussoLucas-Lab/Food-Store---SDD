## Context

Change 5 entregó ingrediente-crud: modelos, repos, validaciones y endpoints para gestionar ingredientes con stock. Change 4 entregó categoria-crud: categorías como clasificadores de productos.

Ahora, Change 6 integra ambos en la entidad central: **Producto**. Un producto es la unidad de venta; tiene precio, categoría(s), y está compuesto por ingredientes con cantidades específicas. El stock disponible de un producto es transitivo: depende del stock de sus ingredientes.

Esto es un change crítico porque introduce:
1. **Nueva relación many-to-many**: Product ↔ Category (un producto puede estar en múltiples categorías; una categoría puede tener múltiples productos)
2. **Nueva relación many-to-many con cantidades**: Product ↔ Ingredient (un producto usa múltiples ingredientes en cantidades específicas)
3. **Validación transitiva de stock**: disponibilidad de un producto = min(stock_disponible / cantidad_requerida para cada ingrediente)
4. **Integridad referencial compleja**: eliminar categoría o ingrediente puede impactar productos

## Goals / Non-Goals

**Goals:**
- Implementar CRUD completo de productos (crear, leer, actualizar, desactivar/eliminar).
- Establecer relaciones many-to-many correctas (Product-Category, Product-Ingredient).
- Calcular stock disponible de forma transparente y coherente.
- Validar integridad referencial: categoría/ingrediente no pueden ser eliminados si hay productos dependientes.
- Endpoints REST totalmente funcionales y documentados.
- Casos de test: alta, edición, baja, consulta, cálculo de stock, validaciones de negocio.

**Non-Goals:**
- Historial de precios o auditoría de cambios (fuera de scope de este change).
- Descuentos, promociones, o variantes de producto (future changes).
- Búsqueda full-text avanzada (usar filtros simples por nombre/categoría en este change).
- Imágenes o galería de productos (future change, UI only).

## Decisions

### Decision 1: Relación Product-Ingredient con cantidades en tabla join
**Choice:** Crear tabla `ProductIngredient(id, product_id, ingredient_id, quantity_required)` con columna `quantity_required`.

**Rationale:** 
- Un producto no usa "el ingrediente" genéricamente, sino X unidades del ingrediente.
- Guardar cantidad en la tabla join (no en el modelo Product) permite flexibilidad: cambiar composición sin duplicar datos.
- Cálculo de stock disponible es: `min(ingredient.stock_disponible / product_ingredient.quantity_required)` para todos los ingredientes del producto.

**Alternatives considered:**
- Guardar cantidad en el modelo Product como JSON: menos queryable, difícil de filtrar en SQL, más complejo de validar.
- Crear subentidades (Variant, CompositionSet): overkill para este change, add complexity sin beneficio claro.

### Decision 2: Stock de producto es READ-ONLY, derivado de ingredientes
**Choice:** El campo `stock_disponible` de un Producto NO es almacenado en la BD; siempre se calcula a partir de ingredientes.

**Rationale:**
- Evita inconsistencias: si actualizamos stock de un ingrediente, el producto se refleja automáticamente.
- Fuente única de verdad: el cambio de stock ocurre en la tabla `ingredients`, no en múltiples lugares.
- Simplifica transacciones: no hay que sincronizar dos registros.

**Trade-off:** 
- Consulta más costosa (join + agregación). Mitigación: index en `product_ingredients(product_id)`, caché en aplicación si es crítico (future optimization).

### Decision 3: Soft delete para productos (status = 'inactive')
**Choice:** Productos nunca se eliminan; se marcan como `status = 'inactive'`.

**Rationale:**
- Productos pueden estar en historial de pedidos completados. Borrar crearían orfandad de datos.
- Auditoría: saber qué producto se vendió en un pedido histórico es requerimiento crítico.

**Hard delete:** Solo si nunca fue usado en pedidos (verificar en lógica de DELETE).

### Decision 4: Validación de integridad: categoría y ingrediente no eliminables si en uso
**Choice:** Antes de eliminar una categoría o ingrediente, verificar si existe algún producto activo que lo use. Si existe, rechazar con error 409 Conflict.

**Rationale:**
- Evita orfandad: no queremos productos sin categoría o composición rota.
- Consistent con modelado: category_id, ingredient_id no son nullable.

**Alternativa:** Cascade delete: eliminar todos los productos que usan la categoría/ingrediente. Rechazado porque pierden datos de pedidos históricos.

### Decision 5: Endpoints y estructura REST
**Choice:** Endpoints siguiendo RESTful conventions:
```
POST   /api/products                 # crear producto
GET    /api/products                 # listar (con filtros: ?category=X, ?status=active)
GET    /api/products/:id             # detalle
PUT    /api/products/:id             # actualizar
DELETE /api/products/:id             # desactivar (soft) o borrar (hard si no está en pedidos)
GET    /api/products/:id/stock       # consultar stock disponible calculado
```

**Rationale:**
- Convención estándar, predecible para clientes frontend.
- Claridad: separar inquietudes (CRUD general vs. cálculo de stock específico).

### Decision 6: Validaciones en request body
**Choice:** Validaciones estrictas al crear/editar:
- `name`: requerido, unique, max 100 chars
- `description`: opcional, max 500 chars
- `base_price`: requerido, > 0, decimal(10, 2)
- `categories`: array requerido, min 1 elemento, cada ID debe existir en BD
- `ingredients`: array requerido, min 1 elemento, cada { ingredient_id, quantity_required } debe existir, quantity_required > 0

**Rationale:**
- Evita datos corruptos en BD.
- Fail-fast: validar en request time, no después.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **Stock calculado es lento si producto usa muchos ingredientes** | Índices en `ProductIngredient(product_id)`. Cache en app si TPS es crítico (pero premature optimization, no implementar ahora). |
| **Cambiar cantidad de un ingrediente en composición puede romper pedidos históricos** | No soportar esto en Change 6. Future decision: versioning de composición o historial. Documentar que cambios de composición afectan cálculos históricos. |
| **Eliminación de ingrediente/categoría accidental rompe integridad** | Validación y errors 409 Conflict lo previenen. Documentar en API. |
| **Frontend necesita múltiples queries para dropdown de categorías e ingredientes** | Aceptable. Si rendimiento crítico (future), implementar caché o query de agregación. |

## Migration Plan

1. **Fase 1 - Migrations SQL:**
   - Crear tablas: `products`, `product_categories`, `product_ingredients`.
   - Crear índices: FK, uniqueness, composite.

2. **Fase 2 - Modelos y Repositories:**
   - Implementar `Product`, `ProductIngredient` modelos en backend/models.
   - Implementar `ProductRepository` con métodos: create, update, getById, listByCategory, delete, checkIfUsedInOrders.
   - Reutilizar `UnitOfWork` de backend-core.

3. **Fase 3 - Services y Validaciones:**
   - Service layer para lógica de negocio: calcular stock, validar integridad, verificar uso en pedidos.
   - Integración con `CategoryRepository` y `IngredientRepository` para validaciones.

4. **Fase 4 - Endpoints:**
   - Implementar todas las rutas REST.
   - Request/response schemas y validaciones.

5. **Fase 5 - Frontend:**
   - Página de listado de productos.
   - Páginas de crear/editar (formularios dinámicos con dropdowns de categorías e ingredientes).
   - Mostrar stock calculado.

6. **Fase 6 - Tests:**
   - Test unitarios: lógica de cálculo de stock, validaciones.
   - Test de integración: CRUD endpoints, integridad relacional.

## Open Questions

- ¿Qué cantidad de categorías máximo puede tener un producto? (propuesta: sin límite en BD, pero validar <= 5 en API por now).
- ¿Necesitamos versionado de precios (historial)? (Fuera de scope por ahora).
- ¿Qué sucede si un producto está en un carrito activo pero el usuario intenta marcarlo inactivo? (Permanecer inactivo; carrito seguirá válido pero no se podrá agregar más unidades. Detalles en Change 8).
