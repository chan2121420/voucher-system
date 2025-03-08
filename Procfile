web: gunicorn management.wsgi:application
worker1: celery --app=management.celery worker -Q --loglevel=info


