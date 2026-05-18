# Food Store

Food Store — e-commerce académico de alimentos (TPI UTN).

---

## Stack

- **Backend**: FastAPI · Python 3.11 · PostgreSQL 15
- **Frontend**: React 18 + TypeScript 5 · Vite 5 · Tailwind CSS
- **Infrastructure**: Docker Compose · Nginx

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Git

---

## Quick Start

1. **Clone the repository**

   ```bash
   git clone <url-del-repo> food-store
   cd food-store
   ```

2. **Copy the environment files**

   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. **Edit `backend/.env`**

   Open `backend/.env` and set at minimum:

   | Variable | What to change |
   |----------|----------------|
   | `SECRET_KEY` | Replace with at least 32 random characters |
   | `DB_USER` / `DB_PASS` / `DB_NAME` | Optional — defaults work for local dev |
   | `MP_ACCESS_TOKEN` / `MP_PUBLIC_KEY` | Optional — replace with your MercadoPago sandbox keys |

4. **Build and start all services**

   ```bash
   docker compose up --build
   ```

5. **Wait for all 3 services to be healthy**

   Docker Compose will start `db`, `backend`, and `frontend`. The backend waits for the database healthcheck before starting. Seed data (admin user + initial catalogue) loads automatically on first run.

6. **The app is ready.**

---

## Service URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

---

## Default Credentials

| Field | Value |
|-------|-------|
| Email | `admin@foodstore.com` |
| Password | `Admin1234!` |

The admin account can manage the catalogue (categories, products, ingredients), view and advance order states, and access system metrics.

To create a client account, register at `/register` with any email and a password that has at least 8 characters, 1 uppercase letter, 1 number, and 1 special character.

---

## Make Targets

| Command | Description |
|---------|-------------|
| `make up` | Build and start the full stack in the background (`docker compose up --build -d`) |
| `make down` | Stop all running services |
| `make logs` | Follow live logs from all services |
| `make seed` | Run the data seed manually (seeds automatically on startup) |
| `make migrate` | Run Alembic migrations inside the backend container |
| `make test` | Run unit tests inside the backend container (excludes integration tests) |
| `make test-cov` | Run unit tests with coverage report (fails if coverage is below 60%) |
| `make test-integration` | Run integration tests only inside the backend container |

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DB_HOST` | Yes | Database host. Use `db` inside Docker Compose, `localhost` outside. |
| `DB_PORT` | Yes | Database port. Default: `5432`. |
| `DB_USER` | Yes | PostgreSQL username. Default: `foodstore`. |
| `DB_PASS` | Yes | PostgreSQL password. Default: `foodstore123`. |
| `DB_NAME` | Yes | Database name. Default: `foodstore_db`. |
| `SECRET_KEY` | Yes | JWT signing key. Must be at least 32 random characters. |
| `JWT_ALGORITHM` | Yes | JWT algorithm. Default: `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | Access token lifetime in minutes. Default: `30`. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Yes | Refresh token lifetime in days. Default: `7`. |
| `ENV` | Yes | Runtime environment. `development` or `production`. |
| `MP_ACCESS_TOKEN` | No | MercadoPago sandbox access token. |
| `MP_PUBLIC_KEY` | No | MercadoPago sandbox public key. |
| `MP_NOTIFICATION_URL` | No | Public URL for MercadoPago IPN webhook callbacks. |
| `CORS_ORIGINS` | Yes | JSON array of allowed CORS origins. Default: `["http://localhost:5173"]`. |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Base URL of the backend API. Default: `http://localhost:8000`. |
| `VITE_API_TIMEOUT` | No | HTTP request timeout in milliseconds. Default: `10000`. |
| `VITE_APP_NAME` | No | Application display name. Default: `Food Store`. |
| `VITE_MP_PUBLIC_KEY` | No | MercadoPago sandbox public key used by the browser SDK. |

> **Note**: The frontend image is built with `VITE_API_URL` and `VITE_MP_PUBLIC_KEY` baked in as build args from `docker-compose.yml`. To change them, update `backend/.env` and rebuild with `docker compose up --build`.

---

## Running Tests

```bash
cd backend && python -m pytest
```

Or using Make (runs inside the Docker container):

```bash
make test        # unit tests only
make test-cov    # unit tests with coverage report (min. 60%)
make test-integration  # integration tests only
```

---

## Stopping the Project

```bash
docker compose down        # stop containers, keep volumes (DB data preserved)
docker compose down -v     # stop containers and delete volumes (resets DB)
```
