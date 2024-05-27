source venv/bin/activate
exec celery -A main beat --pool=solo --loglevel=info
