source venv/bin/activate

echo "Collecting static files..."
python manage.py collectstatic --noinput
deactivate

echo "Build completed."
