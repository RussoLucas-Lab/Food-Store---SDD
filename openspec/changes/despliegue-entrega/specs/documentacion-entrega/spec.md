## ADDED Requirements

### Requirement: README completo en raíz
El repositorio SHALL tener un `README.md` en raíz que permita al corrector levantar el sistema, entenderlo y usarlo sin documentación adicional.

#### Scenario: Secciones obligatorias presentes
- **WHEN** el corrector abre el README
- **THEN** el documento incluye: descripción del sistema, stack tecnológico, prerequisitos, pasos de setup, credenciales de prueba (admin y cliente), estructura del proyecto y checklist de entrega CE verificado

#### Scenario: Setup funciona siguiendo el README
- **WHEN** el corrector sigue los pasos del README en una máquina limpia con Docker
- **THEN** el sistema levanta y el corrector puede iniciar sesión como admin y como cliente

#### Scenario: Credenciales de prueba documentadas
- **WHEN** el corrector busca cómo hacer login
- **THEN** el README provee email y contraseña para el usuario admin (`admin@foodstore.com / Admin1234!`) y para un cliente de prueba

### Requirement: Checklist de entrega verificado
El sistema SHALL cumplir los puntos CE-04 a CE-13 de la rúbrica antes de la entrega.

#### Scenario: CE-04 — Migraciones en BD limpia
- **WHEN** se ejecuta `alembic upgrade head` en una BD vacía
- **THEN** el comando termina sin errores y todas las tablas se crean correctamente

#### Scenario: CE-05 — Seed idempotente
- **WHEN** se ejecuta `python -m app.db.seed` una o más veces
- **THEN** los datos iniciales están presentes y no se duplican

#### Scenario: CE-10 — Sin commits directos en services
- **WHEN** se audita el código de la capa service
- **THEN** ningún archivo `service.py` llama directamente a `session.commit()` o `session.rollback()`

#### Scenario: CE-11 — Stores Zustand tipados
- **WHEN** se revisa el frontend
- **THEN** existen exactamente 4 stores Zustand (authStore, cartStore, paymentStore, uiStore) con tipos TypeScript y persist correcto donde corresponde

#### Scenario: CE-13 — Video demostración referenciado
- **WHEN** el corrector lee el README
- **THEN** hay un link a un video de demostración de 5-10 minutos que muestra el flujo completo de la aplicación

### Requirement: .gitignore actualizado
El repositorio SHALL tener un `.gitignore` que excluya archivos `.env`, `__pycache__`, `node_modules`, `dist/` y volúmenes de Docker.

#### Scenario: Archivos sensibles no trackeados
- **WHEN** el desarrollador ejecuta `git status` después de crear los `.env`
- **THEN** los archivos `.env` no aparecen en los archivos a commitear
