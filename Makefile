.PHONY: up down logs migrate seed test test-cov test-integration

# ============================================================================
# Docker Compose — operaciones del stack completo
# ============================================================================

up:
	docker compose up --build -d

down:
	docker compose down

# El seed se ejecuta automáticamente al iniciar el backend.
# Este target lo corre manualmente si necesitás reiniciar los datos.
seed:
	docker compose exec backend python -m backend.db.seed

migrate:
	docker compose exec backend alembic upgrade head

logs:
	docker compose logs -f

# ============================================================================
# Tests (ejecutar dentro del contenedor)
# ============================================================================

# Run all unit tests (exclude integration)
test:
	docker compose exec backend pytest backend/tests -m "not integration" -v

# Run tests with coverage, fail if under 60%
test-cov:
	docker compose exec backend pytest backend/tests -m "not integration" --cov=backend --cov-report=term-missing --cov-fail-under=60 -v

# Run integration tests only
test-integration:
	docker compose exec backend pytest backend/tests -m "integration" -v
