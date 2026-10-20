#!/bin/sh
set -eu
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py bootstrap_content
if [ "${SEED_DEMO:-false}" = "true" ]; then
    python manage.py seed_demo
fi
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 90 --access-logfile - --error-logfile -
