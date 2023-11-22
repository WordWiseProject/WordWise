release: python manage.py migrate
web: gunicorn config.wsgi:application
heroku run python manage.py createsuperuser
