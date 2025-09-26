#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Set the Django settings module environment variable
export DJANGO_SETTINGS_MODULE=config.settings.prod

# Create the static directory
mkdir -p /app/static

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

#Pull from stripe database
echo "Pulling From Stripe Database..."
python manage.py pull_stripe

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Add Cron Jobs
echo "Adding Cron jobs..."
python manage.py crontab add

# Show Cron Jobs
echo "Current Cron jobs:"
python manage.py crontab show

# Start the cron service (if needed)
echo "Starting cron service..."
service cron start

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
