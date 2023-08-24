#!/bin/sh


python manage.py migrate;
python manage.py collectstatic --noinput;
gunicorn -w 2 -b 0:8000 foodgram.wsgi;
