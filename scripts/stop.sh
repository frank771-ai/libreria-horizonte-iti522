#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

sudo -S docker-compose down
echo "Horizonte Inventory detenido. Los datos permanecen en el volumen horizonte_inventory_data."
