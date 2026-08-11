#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/StockSwap-backend"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

cd "$BACKEND_DIR"

"$PYTHON_BIN" -m pip install --upgrade pip >/dev/null 2>&1 || true
"$PYTHON_BIN" -m pip install -r requirements.txt

"$PYTHON_BIN" manage.py migrate --noinput
"$PYTHON_BIN" manage.py collectstatic --noinput || true

exec "$PYTHON_BIN" -m gunicorn StockSwap_main.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers "${WEB_CONCURRENCY:-2}"
