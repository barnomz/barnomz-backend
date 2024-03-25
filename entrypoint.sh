# Entry point script for Django with Docker

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start Gunicorn server
echo "Starting Gunicorn..."
exec gunicorn your_project_name.wsgi:application --bind 0.0.0.0:8000