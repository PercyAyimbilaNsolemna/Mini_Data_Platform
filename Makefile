.PHONY: help up down logs ps build clean validate health test

help:
	@echo "Mini Data Platform - Available Commands"
	@echo "========================================"
	@echo "make up              - Start all services"
	@echo "make down            - Stop all services"
	@echo "make ps              - Show running services"
	@echo "make logs            - View service logs"
	@echo "make build           - Build Docker image"
	@echo "make health          - Check service health status"
	@echo "make clean           - Clean volumes and data"
	@echo "make validate        - Validate docker-compose configuration"
	@echo "make test            - Run tests"

build:
	@echo "Building Docker image..."
	docker-compose build --no-cache

up:
	@echo "Starting Mini Data Platform services..."
	docker-compose up -d
	@echo "Waiting for services to become healthy..."
	@sleep 10
	@make health

down:
	@echo "Stopping Mini Data Platform services..."
	docker-compose down

ps:
	@echo "Running services:"
	docker-compose ps

logs:
	docker-compose logs -f

health:
	@echo "Checking service health status..."
	@docker-compose ps | grep -E 'postgres|airflow|minio|metabase'
	@echo "\nService Health Summary:"
	@docker-compose exec -T postgres pg_isready -U postgres -h localhost && echo "✓ PostgreSQL healthy" || echo "✗ PostgreSQL unhealthy"
	@docker-compose exec -T minio curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1 && echo "✓ MinIO healthy" || echo "✗ MinIO unhealthy"
	@docker-compose exec -T airflow curl -f http://localhost:8080/health > /dev/null 2>&1 && echo "✓ Airflow healthy" || echo "✗ Airflow unhealthy"
	@docker-compose exec -T metabase curl -f http://localhost:3000/api/health > /dev/null 2>&1 && echo "✓ Metabase healthy" || echo "✗ Metabase unhealthy"

validate:
	@echo "Validating docker-compose configuration..."
	docker-compose config > /dev/null
	@echo "✓ Configuration is valid"

clean:
	@echo "Removing volumes and data..."
	docker-compose down -v
	@echo "✓ Cleanup complete"

test:
	@echo "Running tests..."
	pytest -v tests/

restart:
	@echo "Restarting all services..."
	docker-compose restart
