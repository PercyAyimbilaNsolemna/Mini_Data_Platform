#!/bin/bash
set -e

log_info() {
  echo "{\"timestamp\":\"$(date -u +'%Y-%m-%dT%H:%M:%SZ')\",\"level\":\"INFO\",\"message\":\"$1\"}"
}

log_error() {
  echo "{\"timestamp\":\"$(date -u +'%Y-%m-%dT%H:%M:%SZ')\",\"level\":\"ERROR\",\"message\":\"$1\"}" >&2
}

# Wait for Postgres to be ready
log_info "Waiting for Postgres..."
until pg_isready -h "${POSTGRES_HOST:-postgres}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER}" >/dev/null 2>&1; do
  sleep 3
done

# Initialize Airflow DB
log_info "Migrating Airflow database..."
airflow db migrate

# Create admin user if not exists
log_info "Creating Airflow admin user..."
airflow users create \
  --username "${AIRFLOW_ADMIN_USERNAME:-admin}" \
  --firstname "Airflow" \
  --lastname "Admin" \
  --role "Admin" \
  --email "admin@airflow.local" \
  --password "${AIRFLOW_ADMIN_PASSWORD:-admin}" 2>/dev/null || log_info "Admin user already exists"

# Start Airflow standalone
log_info "Starting Airflow standalone..."
exec airflow standalone