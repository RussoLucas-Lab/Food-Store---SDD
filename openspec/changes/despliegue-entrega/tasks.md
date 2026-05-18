## 1. Dockerización del Backend

- [x] 1.1 Crear `backend/Dockerfile` multi-stage (builder instala deps, runner corre uvicorn en puerto 8000)
- [x] 1.2 Agregar `.dockerignore` en `backend/` excluyendo `__pycache__`, `.env`, `*.pyc`, `.venv`
- [x] 1.3 Crear `backend/.env.example` con todas las variables requeridas documentadas con comentarios

## 2. Dockerización del Frontend

- [x] 2.1 Crear `frontend/Dockerfile` con stage de build (`npm run build`) y stage de serve (`nginx:alpine`)
- [x] 2.2 Crear `frontend/nginx.conf` con configuración de SPA (fallback a `index.html` para rutas del router)
- [x] 2.3 Agregar `.dockerignore` en `frontend/` excluyendo `node_modules`, `dist`, `.env`
- [x] 2.4 Crear `frontend/.env.example` con `VITE_API_URL` y `VITE_MP_PUBLIC_KEY` documentados

## 3. Docker Compose

- [x] 3.1 Crear `docker-compose.yml` en raíz con servicios: `backend`, `frontend` (app usa in-memory, no requiere DB externa)
- [x] 3.2 Configurar `db` con healthcheck, volumen persistente y variables `POSTGRES_*` (N/A — app in-memory)
- [x] 3.3 Configurar `backend` con variables de entorno desde `.env`
- [x] 3.4 Configurar `frontend` con `depends_on: backend`, variable `VITE_API_URL` apuntando al backend
- [x] 3.5 Mapear puertos: backend→8000, frontend→5173

## 4. Makefile

- [x] 4.1 Agregar/actualizar target `up`: `docker compose up --build -d`
- [x] 4.2 Agregar/actualizar target `down`: `docker compose down`
- [x] 4.3 Agregar target `migrate` (N/A — app in-memory; seed automático en startup)
- [x] 4.4 Agregar target `seed`: `docker compose exec backend python -m backend.db.seed`
- [x] 4.5 Agregar target `logs`: `docker compose logs -f`
- [x] 4.6 Agregar target `test`: `docker compose exec backend pytest`

## 5. Verificación del Checklist de Entrega

- [x] 5.1 CE-04: Verificado — app usa in-memory; seed carga datos al arrancar sin errores
- [x] 5.2 CE-05: Verificado — `backend/db/seed.py` es idempotente (verifica existencia antes de insertar)
- [x] 5.3 CE-10: Auditado — ningún `service.py` llama `session.commit()` directamente
- [x] 5.4 CE-11: Verificado — 4 stores en `frontend/src/shared/stores/` con persist donde corresponde
- [ ] 5.5 CE-13: Grabar y subir el video de demostración (5-10 min) y agregar link en README

## 6. README

- [x] 6.1 Crear/reemplazar `README.md` en raíz con sección de descripción del sistema y stack tecnológico
- [x] 6.2 Agregar sección de prerequisitos (Docker Desktop)
- [x] 6.3 Agregar sección de setup paso a paso: clonar → copiar .env → `make up`
- [x] 6.4 Agregar sección de credenciales de prueba: admin (`admin@foodstore.com / Admin1234!`) y cliente de prueba
- [x] 6.5 Agregar sección de estructura del proyecto (árbol de directorios con descripción)
- [x] 6.6 Agregar checklist CE verificado y placeholder para link al video de demostración

## 7. Prueba de Smoke End-to-End

- [ ] 7.1 Copiar `backend/.env.example` a `.env` en raíz y ejecutar `make up`
- [ ] 7.2 Verificar que `GET http://localhost:8000/health` responde 200
- [ ] 7.3 Verificar que `http://localhost:5173` carga el frontend sin errores de consola
- [ ] 7.4 Verificar login como admin (`admin@foodstore.com / Admin1234!`) en el frontend
- [ ] 7.5 Corregir cualquier error encontrado en el smoke test
