source venv/bin/activate
exec celery -A main worker --pool=solo --loglevel=info
