#!/bin/sh

#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done

echo "PostgreSQL is available."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application \
        --bind 0.0.0.0:8002 \
        --workers 3 \
        --threads 2 \
        --timeout 120