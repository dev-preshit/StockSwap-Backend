#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/StockSwap-backend"

cd "$BACKEND_DIR"

python -m pip install --upgrade pip >/dev/null 2>&1 || true
pip install -r requirements.txt

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

exec gunicorn StockSwap_main.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers "${WEB_CONCURRENCY:-2}"
