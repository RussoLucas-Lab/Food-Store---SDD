## Context

El backend de Food Store fue construido con una organización por tipo técnico: `models/`, `repositories/`, `uow/`, `config/` en el raíz del proyecto, y `backend/services/`, `backend/routers/`, `backend/schemas/` dentro de `backend/`. Esta estructura diverge del diseño definido en CLAUDE.md, que establece una arquitectura feature-first con módulos por dominio.

La exploración previa identificó ~75–80 archivos afectados, sin dependencias circulares en la estructura target, y sin cambios de lógica requeridos. El mayor riesgo es la actualización masiva de imports.

Stack: FastAPI · SQLModel · Python 3.12. Sin ORM con migraciones Alembic activas aún (modelo en memoria + PostgreSQL pendiente de activar).

## Goals / Non-Goals

**Goals:**
- Mover todo el código Python del backend a `backend/modules/<feature>/` (model, repository, service, schemas, router por módulo)
- Centralizar componentes transversales en `backend/core/` (UoW, seguridad, configuración)
- Actualizar todos los imports en código y tests para que la suite pase sin modificar lógica
- Dejar `carrito-pedidos` y los changes siguientes con una base estructural correcta

**Non-Goals:**
- Cambiar lógica de negocio, validaciones o comportamiento de APIs
- Agregar tests nuevos (solo reubicar los existentes)
- Activar SQLAlchemy/Alembic (eso es otro change)
- Modificar el frontend

## Decisions

### D1: UoW centralizado en `backend/core/`, no por feature

**Decisión**: El Unit of Work vive en `backend/core/uow.py` (interfaz) y `backend/core/uow_inmemory.py` (implementación), no dentro de ningún módulo.

**Rationale**: `PedidoService` necesita acceder a `ProductRepository` e `IngredienteRepository` cross-feature. Si el UoW fuera feature-specific, habría imports cruzados entre módulos (violación de la arquitectura FSD). El UoW centralizado orquesta repositorios de múltiples features sin crear dependencias circulares.

**Alternativa descartada**: UoW por feature → genera acoplamiento horizontal entre módulos.

---

### D2: `backend/core/security.py` unifica PasswordService y TokenService

**Decisión**: `password_service.py` y `token_service.py` se fusionan en `backend/core/security.py`.

**Rationale**: Ambos son servicios transversales sin lógica de dominio específica. No pertenecen a ningún feature en particular. Fusionarlos reduce la cantidad de imports en middleware y routers.

**Alternativa descartada**: Mantenerlos separados → dos archivos en core/ con responsabilidad análoga y sin razón para estar separados.

---

### D3: Auth como módulo normal con UoW

**Decisión**: `backend/modules/auth/` sigue el mismo patrón que los demás módulos. El router de auth accede a `UsuarioRepository` a través del UoW, eliminando la instanciación directa de `InMemoryUsuarioRepository` que existe hoy.

**Rationale**: La instanciación directa en el router es una inconsistencia con el resto del código. Migrar al patrón UoW hace auth predecible y testeable de la misma manera que categorias, clientes, etc.

**Alternativa descartada**: Dejar auth con acceso directo al repo → perpetúa la inconsistencia.

---

### D4: Tests reorganizados en `backend/tests/` con estructura espejo

**Decisión**: Los tests de `/tests` (root) y `/backend/tests` se consolidan en `backend/tests/` con subdirectorios que espejean los módulos: `backend/tests/modules/auth/`, `backend/tests/modules/categorias/`, etc.

**Rationale**: Facilita encontrar el test de cada módulo y permite conftest.py por módulo si es necesario. Elimina la confusión de tener dos carpetas de tests en distintos niveles.

---

### D5: Migración en 6 fases progresivas, sin big bang

**Decisión**: El refactor se ejecuta fase por fase con un checkpoint de compilación/tests entre cada una:

```
Fase 1 → Crear backend/core/ (sin tocar features)
Fase 2 → Mover models/ → modules/*/model.py
Fase 3 → Mover repositories/ → modules/*/repository.py
Fase 4 → Mover services/ → modules/*/service.py
Fase 5 → Mover routers/ + schemas/ → modules/*/router.py + schemas.py · actualizar main.py
Fase 6 → Consolidar tests · eliminar directorios viejos
```

**Rationale**: Permite detectar errores de imports de forma localizada por fase. Cada checkpoint valida que `uvicorn backend.main:app` arranca y los tests del módulo migrado pasan.

**Alternativa descartada**: Mover todo de una vez → dificulta identificar la causa de errores.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| Imports rotos en cascada al mover archivos | Migración fase a fase; checkpoint de arranque del servidor entre cada fase |
| Tests que testean rutas de imports (no comportamiento) | Identificar en Fase 6; actualizar sin cambiar aserciones de comportamiento |
| UoW inmemory instanciado a nivel de módulo en los routers actuales | Reemplazar con dependency injection vía FastAPI `Depends()` en Fase 5 |
| `auth.py` instancia `InMemoryUsuarioRepository()` directamente | Migrar a UoW en Fase 5 junto con el resto de routers |
| Olvidar actualizar algún import | Buscar con grep `from models.`, `from repositories.`, `from uow.`, `from config.` al final de cada fase |

## Migration Plan

1. Crear rama `refactor/feature-first` desde `main`
2. Ejecutar fases 1–6 con commits por fase (mínimo un commit por fase)
3. Al final de cada fase: `python -m pytest` + arrancar servidor manualmente
4. Al terminar Fase 6: ejecutar suite completa, verificar que no queda ningún import desde los directorios viejos
5. PR a `main` con descripción del refactor

**Rollback**: Al ser un branch dedicado, revertir es simplemente descartar el branch. No hay cambios de datos ni migraciones de BD.

## Open Questions

- ¿Se mantiene `repositories/inmemory.py` (base vacía) o se elimina directamente? → Eliminarlo; ningún repo lo importa con lógica real.
- ¿`postgresql_usuario_repository.py` se mueve a `backend/modules/auth/` o a `backend/core/`? → `backend/modules/auth/` porque es la implementación PostgreSQL del repo de usuarios.
