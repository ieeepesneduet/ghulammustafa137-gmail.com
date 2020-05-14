web: gunicorn app:app
worker: celery worker -A tasks.celeryapp -l INFO