source venv/bin/activate
exec celery -A main beat --loglevel=info
