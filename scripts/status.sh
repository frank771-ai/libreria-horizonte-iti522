#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

sudo -S docker-compose ps
echo
curl --silent --show-error http://127.0.0.1:8080/health || true
echo
