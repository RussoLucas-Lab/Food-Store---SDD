# Tasks: Refactor Categoría e Ingrediente para Service Layer

## 1. CategoryService Implementation

- [x] 1.1 Create `backend/services/categoria_service.py` with CategoryService class
- [x] 1.2 Implement CategoryService.create_categoria(nombre, descripcion) with validation
- [x] 1.3 Implement CategoryService.update_categoria(id, nombre, descripcion) with duplicate check
- [x] 1.4 Implement CategoryService.delete_categoria(id) with product usage check (409 if in use)
- [x] 1.5 Implement CategoryService.get_categoria(id)
- [x] 1.6 Implement CategoryService.list_categorias(skip, limit, search)

## 2. IngredientService Implementation

- [x] 2.1 Create `backend/services/ingrediente_service.py` with IngredientService class
- [x] 2.2 Implement IngredientService.create_ingrediente(...) with all validations
- [x] 2.3 Implement IngredientService.update_ingrediente(id, ...) with duplicate check
- [x] 2.4 Implement IngredientService.delete_ingrediente(id) with product usage check (409 if in use)
- [x] 2.5 Implement IngredientService.get_ingrediente(id)
- [x] 2.6 Implement IngredientService.list_ingredientes(skip, limit, search, unidad_medida, categoria_id)
- [x] 2.7 Implement IngredientService.get_stock_history(id)

## 3. Repository Updates (if needed)

- [x] 3.1 Verify CategoryRepository has count_by_category() method or add it
- [x] 3.2 Verify IngredientRepository has count_by_ingredient() method or add it
- [x] 3.3 Verify ProductRepository has count_by_category(categoria_id) and count_by_ingredient(ingrediente_id) methods
- [x] 3.4 If methods missing, add them to InMemory implementations

## 4. Router Refactoring: Categorías

- [x] 4.1 Update `backend/routers/categorias.py` POST endpoint — use CategoryService.create_categoria()
- [x] 4.2 Update GET endpoint (list) — use CategoryService.list_categorias()
- [x] 4.3 Update GET /:id endpoint — use CategoryService.get_categoria()
- [x] 4.4 Update PUT /:id endpoint — use CategoryService.update_categoria()
- [x] 4.5 Update DELETE /:id endpoint — use CategoryService.delete_categoria()
- [x] 4.6 Add exception mapping: ValueError → HTTPException (400, 404, or 409)
- [x] 4.7 Remove all business logic from categorias.py router (keep only HTTP concerns)

## 5. Router Refactoring: Ingredientes

- [x] 5.1 Update `backend/routers/ingredientes.py` POST endpoint — use IngredientService.create_ingrediente()
- [x] 5.2 Update GET endpoint (list) — use IngredientService.list_ingredientes()
- [x] 5.3 Update GET /buscar endpoint — use IngredientService.list_ingredientes() with search
- [x] 5.4 Update GET /:id endpoint — use IngredientService.get_ingrediente()
- [x] 5.5 Update PUT /:id endpoint — use IngredientService.update_ingrediente()
- [x] 5.6 Update DELETE /:id endpoint — use IngredientService.delete_ingrediente()
- [x] 5.7 Update GET /:id/historial-stock endpoint — use IngredientService.get_stock_history()
- [x] 5.8 Add exception mapping: ValueError → HTTPException (400, 404, or 409)
- [x] 5.9 Remove all business logic from ingredientes.py router

## 6. Unit Tests: CategoryService

- [x] 6.1 Create `backend/tests/test_categoria_service.py`
- [x] 6.2 Test create_categoria() valid input
- [x] 6.3 Test create_categoria() duplicate name → ValueError
- [x] 6.4 Test create_categoria() empty name → ValueError
- [x] 6.5 Test update_categoria() valid input
- [x] 6.6 Test update_categoria() id not found → ValueError
- [x] 6.7 Test update_categoria() duplicate name (different category) → ValueError
- [x] 6.8 Test delete_categoria() not in use → success
- [x] 6.9 Test delete_categoria() in use by products → ValueError
- [x] 6.10 Test delete_categoria() id not found → ValueError
- [x] 6.11 Test get_categoria() valid id → returns DTO
- [x] 6.12 Test get_categoria() invalid id → ValueError
- [x] 6.13 Test list_categorias() no filters → returns paginated list
- [x] 6.14 Test list_categorias() with search → filters results
- [x] 6.15 Verify coverage > 90%

## 7. Unit Tests: IngredientService

- [x] 7.1 Create `backend/tests/test_ingrediente_service.py`
- [x] 7.2 Test create_ingrediente() valid input
- [x] 7.3 Test create_ingrediente() duplicate name → ValueError
- [x] 7.4 Test create_ingrediente() invalid unidad_medida → ValueError
- [x] 7.5 Test create_ingrediente() negative stock → ValueError
- [x] 7.6 Test update_ingrediente() valid input
- [x] 7.7 Test update_ingrediente() negative stock → ValueError
- [x] 7.8 Test delete_ingrediente() not in use → success
- [x] 7.9 Test delete_ingrediente() in use by products → ValueError
- [x] 7.10 Test delete_ingrediente() id not found → ValueError
- [x] 7.11 Test get_ingrediente() valid id → returns DTO
- [x] 7.12 Test get_ingrediente() invalid id → ValueError
- [x] 7.13 Test list_ingredientes() with filters (unidad_medida, categoria_id, search)
- [x] 7.14 Test get_stock_history() valid id → returns list
- [x] 7.15 Test get_stock_history() invalid id → ValueError
- [x] 7.16 Verify coverage > 90%

## 8. Integration Tests: Categorías Router

- [x] 8.1 Create `backend/tests/test_categoria_endpoints.py`
- [x] 8.2 Test POST /categorias valid → 201 with DTO
- [x] 8.3 Test POST /categorias duplicate name → 409
- [x] 8.4 Test POST /categorias empty name → 400
- [x] 8.5 Test GET /categorias list → 200 with list
- [x] 8.6 Test GET /categorias/:id valid → 200 with DTO
- [x] 8.7 Test GET /categorias/:id not found → 404
- [x] 8.8 Test PUT /categorias/:id valid → 200 with updated DTO
- [x] 8.9 Test PUT /categorias/:id duplicate name → 409
- [x] 8.10 Test DELETE /categorias/:id not in use → 200 with soft-deleted DTO
- [x] 8.11 Test DELETE /categorias/:id in use by products → 409
- [x] 8.12 Test DELETE /categorias/:id not found → 404
- [x] 8.13 Verify all tests pass

## 9. Integration Tests: Ingredientes Router

- [x] 9.1 Create `backend/tests/test_ingrediente_endpoints.py`
- [x] 9.2 Test POST /ingredientes valid → 201 with DTO
- [x] 9.3 Test POST /ingredientes duplicate name → 409
- [x] 9.4 Test POST /ingredientes invalid unidad_medida → 400
- [x] 9.5 Test POST /ingredientes negative stock → 400
- [x] 9.6 Test GET /ingredientes list → 200 with paginated list
- [x] 9.7 Test GET /ingredientes/buscar search → 200 with filtered results
- [x] 9.8 Test GET /ingredientes/:id valid → 200 with DTO
- [x] 9.9 Test GET /ingredientes/:id not found → 404
- [x] 9.10 Test PUT /ingredientes/:id valid → 200 with updated DTO
- [x] 9.11 Test DELETE /ingredientes/:id not in use → 200 with soft-deleted DTO
- [x] 9.12 Test DELETE /ingredientes/:id in use by products → 409
- [x] 9.13 Test GET /ingredientes/:id/historial-stock → 200 with history list
- [x] 9.14 Verify all tests pass

## 10. Code Review & Cleanup

- [x] 10.1 Verify no business logic remains in categorias.py router
- [x] 10.2 Verify no business logic remains in ingredientes.py router
- [ ] 10.3 Run all existing tests to ensure no regressions
- [ ] 10.4 Verify API contracts identical (same responses, error codes)
- [ ] 10.5 Code review: CategoryService + IngredientService for correctness
- [ ] 10.6 Verify UoW injection is clean (no globals)

## 11. Documentation & Commit

- [ ] 11.1 Update README with CategoryService/IngredientService documentation
- [x] 11.2 Add docstrings to all service methods
- [ ] 11.3 Create git commit: "refactor: extract CategoryService and IngredientService from routers"
- [ ] 11.4 Verify commit includes all service + router files
- [ ] 11.5 Archive Change 7 (refactor-categoria-ingrediente)

---

## Summary

**Total Tasks**: 71
**Grouped by**:
- Section 1: CategoryService impl (6 tasks)
- Section 2: IngredientService impl (7 tasks)
- Section 3: Repo verification (4 tasks)
- Section 4-5: Router refactoring (16 tasks)
- Section 6-7: Unit tests (31 tasks)
- Section 8-9: Integration tests (26 tasks)
- Section 10-11: Review + docs (5 tasks)

**Estimated Time**: 4-5 hours
- Services: 1 hour
- Routers: 30 min
- Unit tests: 1.5 hours
- Integration tests: 1.5 hours
- Review + commit: 30 min
