#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
project_dir="$PWD"
export LD_LIBRARY_PATH="$project_dir/.local/postgres/usr/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
pg_bin="$project_dir/.local/postgres/usr/bin"
if ! "$pg_bin/pg_ctl" -D "$project_dir/.local/pgdata" status >/dev/null 2>&1; then
    "$pg_bin/pg_ctl" -D "$project_dir/.local/pgdata" \
        -l "$project_dir/.local/postgres.log" \
        -o "-h 127.0.0.1 -p 5433 -k $project_dir/.local" start
fi
.venv/bin/python manage.py migrate --noinput
exec .venv/bin/python manage.py runserver 127.0.0.1:8000
