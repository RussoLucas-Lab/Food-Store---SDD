## Context

El stack es FastAPI + PostgreSQL (backend) y React/Vite (frontend). Todo el código de aplicación está implementado (changes 1-13). Existe un `Makefile` básico en raíz. El proyecto se entrega como TPI académico: el corrector sigue el README en una máquina limpia y espera poder levantar el sistema con el mínimo de pasos. La penalización por fallo de setup es -30%.

## Goals / Non-Goals

**Goals:**
- El sistema levanta con `docker compose up` o con `make up` en una máquina limpia.
- El README permite al corrector registrarse, iniciar sesión y explorar el sistema sin documentación adicional.
- El checklist CE-04 a CE-13 está verificado y corregido donde sea necesario.
- Los `.env.example` documentan todas las variables obligatorias.

**Non-Goals:**
- Despliegue a producción en la nube (es opcional para el bonus de +10 pts).
- CI/CD automatizado (no requerido por la rúbrica).
- Optimización de imágenes Docker para producción.

## Decisions

### D-01: Docker Compose como método de setup primario

**Decisión**: `docker-compose.yml` con tres servicios — `db` (postgres:15), `backend` (FastAPI), `frontend` (Nginx sirviendo el build de Vite).

**Alternativas consideradas**:
- Setup manual (pip install + npm install): requiere que el corrector tenga Python y Node instalados con versiones exactas → muy frágil.
- Solo Dockerizar el backend: el frontend quedaría sin setup reproducible.

**Razón**: Docker garantiza reproducibilidad total. El corrector solo necesita Docker Desktop.

### D-02: Frontend servido por Nginx en Docker

**Decisión**: El frontend se compila con `npm run build` en el Dockerfile y el artefacto estático es servido por `nginx:alpine`.

**Razón**: Es el patrón estándar para Vite en producción. Evita tener Node.js en la imagen final. La API URL se inyecta como variable de entorno en tiempo de build via `VITE_API_URL`.

### D-03: Makefile como interfaz de operaciones

**Decisión**: El `Makefile` existente se expande con targets: `up`, `down`, `migrate`, `seed`, `logs`, `test`.

**Razón**: Estandariza los comandos más comunes. El README referencia `make <target>` en lugar de comandos largos de docker.

### D-04: Variables de entorno con valores de desarrollo pre-cargados en `.env.example`

**Decisión**: Los `.env.example` incluyen valores funcionales para desarrollo local (no producción): SECRET_KEY de ejemplo, credenciales de BD, claves MP de sandbox.

**Razón**: Reduce fricción de setup. El corrector puede copiar `.env.example` a `.env` directamente para levantar el sistema. Las claves de MP son de sandbox (no hay riesgo financiero).

### D-05: Verificación del checklist CE como tarea de auditoría pre-entrega

**Decisión**: Se revisa el código contra CE-04, CE-05, CE-10, CE-11, CE-13 y se corrige cualquier incumplimiento encontrado.

**Razón**: La rúbrica pena directamente por estos puntos; conviene auditarlos explícitamente antes de la entrega.

## Risks / Trade-offs

- **[Riesgo] VITE_API_URL hardcodeada en build**: Si el corrector cambia el puerto del backend, debe rebuilddear el frontend. → Mitigación: documentar en README. Alternativa: usar variable runtime vía `window.__env__` (descartada por complejidad).
- **[Riesgo] Migraciones fallan en BD limpia**: Si hay migraciones de Alembic con errores de dependencia, `alembic upgrade head` falla. → Mitigación: probar CE-04 en contenedor limpio como parte de las tareas.
- **[Riesgo] Puertos en uso**: El corrector puede tener algo en puerto 5432 o 8000. → Mitigación: documentar cómo cambiar puertos en `.env`.

## Migration Plan

1. Probar `docker compose up` en limpio (sin volúmenes previos).
2. Ejecutar `make migrate && make seed` dentro del contenedor.
3. Verificar que `/api/v1/health` responde 200 y el frontend carga.
4. Verificar login con `admin@foodstore.com / Admin1234!`.
5. Rollback: `docker compose down -v` elimina todo.
