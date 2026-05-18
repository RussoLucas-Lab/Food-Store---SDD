## ADDED Requirements

### Requirement: Stack levanta con Docker Compose
El sistema SHALL poder levantarse completamente ejecutando `docker compose up` (o `make up`) desde la raíz del repositorio en una máquina con solo Docker Desktop instalado.

#### Scenario: Levantamiento desde cero
- **WHEN** el usuario clona el repositorio, copia los `.env.example` a `.env` y ejecuta `docker compose up --build`
- **THEN** los tres servicios (db, backend, frontend) arrancan sin errores y el frontend es accesible en `http://localhost:5173` y el backend en `http://localhost:8000`

#### Scenario: Health check del backend
- **WHEN** el backend levanta correctamente
- **THEN** `GET /api/v1/health` responde HTTP 200

#### Scenario: Migraciones y seed
- **WHEN** el usuario ejecuta `make migrate && make seed` (o los comandos equivalentes de docker exec)
- **THEN** `alembic upgrade head` termina sin errores y la BD contiene los datos seed (roles, estados de pedido, admin)

### Requirement: Archivos de entorno de ejemplo
El repositorio SHALL incluir `.env.example` en `backend/` y `frontend/` con valores funcionales para desarrollo local.

#### Scenario: Copia directa funciona
- **WHEN** el usuario copia `backend/.env.example` a `backend/.env` y `frontend/.env.example` a `frontend/.env` sin modificar nada
- **THEN** el sistema levanta correctamente en modo desarrollo local

#### Scenario: Documentación de variables
- **WHEN** el usuario revisa `.env.example`
- **THEN** cada variable tiene un comentario que explica para qué sirve

### Requirement: Makefile de operaciones
El proyecto SHALL incluir un `Makefile` en raíz con los targets: `up`, `down`, `migrate`, `seed`, `logs`, `test`.

#### Scenario: Target up
- **WHEN** el usuario ejecuta `make up`
- **THEN** se ejecuta `docker compose up --build -d` y los servicios arrancan en segundo plano

#### Scenario: Target down
- **WHEN** el usuario ejecuta `make down`
- **THEN** se ejecuta `docker compose down` y los servicios se detienen

#### Scenario: Target migrate
- **WHEN** el usuario ejecuta `make migrate`
- **THEN** se ejecuta `alembic upgrade head` dentro del contenedor del backend

#### Scenario: Target seed
- **WHEN** el usuario ejecuta `make seed`
- **THEN** se ejecuta `python -m app.db.seed` dentro del contenedor del backend

### Requirement: Dockerfile del backend
El backend SHALL tener un `Dockerfile` multi-stage que instala dependencias y corre Uvicorn.

#### Scenario: Build sin errores
- **WHEN** se ejecuta `docker build -f backend/Dockerfile .`
- **THEN** la imagen se construye sin errores y el contenedor arranca en el puerto 8000

### Requirement: Dockerfile del frontend
El frontend SHALL tener un `Dockerfile` que compila el build de Vite y lo sirve con Nginx.

#### Scenario: Build y serve
- **WHEN** se ejecuta `docker build -f frontend/Dockerfile .` con `VITE_API_URL` definido
- **THEN** la imagen compilada sirve el frontend en el puerto 80 vía Nginx
