#!/bin/bash
set -eu

API_HOST=0.0.0.0
API_PORT=${API_PORT:-5000}
API_WORKERS=${API_WORKERS:-3}
API_WORKER_MAX_REQUESTS=${API_WORKER_MAX_REQUESTS:-10000}

case "$1" in
    api) poetry run gunicorn immuni_otp.sanic:sanic_app \
            --access-logfile='-' \
            --bind=${API_HOST}:${API_PORT} \
            --logger-class=immuni_common.helpers.logging.CustomGunicornLogger \
            --max-requests=${API_WORKER_MAX_REQUESTS} \
            --workers=${API_WORKERS} \
            --worker-class=immuni_common.uvicorn.ImmuniUvicornWorker ;;
    debug) echo "Running in debug mode ..." \
            && tail -f /dev/null ;;  # Allow entering the container to inspect the environment.
    *) echo "Received unknown command $1 (allowed: api)"
       exit 2 ;;
esac
