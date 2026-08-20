#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if [[ ! -f .env ]]; then
  umask 077
  generated_password="$(openssl rand -hex 24)"
  sed "s/^DB_PASSWORD=.*/DB_PASSWORD=${generated_password}/" .env.example > .env
  unset generated_password
  echo "Archivo .env local creado con una contraseña aleatoria"
fi

mkdir -p logs
touch logs/application.log
chmod 600 .env logs/application.log

echo "Iniciando PostgreSQL y Horizonte Inventory..."
sudo -S docker-compose up -d --build

echo "Esperando el endpoint /health..."
for attempt in {1..40}; do
  if curl --silent --fail http://127.0.0.1:8080/health >/dev/null; then
    echo "Horizonte Inventory está disponible en http://localhost:8080"
    echo "Salud: http://localhost:8080/health"
    exit 0
  fi
  sleep 2
done

echo "La aplicación no respondió dentro del tiempo esperado." >&2
sudo -S docker-compose ps
exit 1
