FROM python:3.7-slim

WORKDIR /app

COPY foodgram .

RUN pip3 install -r requirements.txt --no-cache-dir

#CMD ["python", "manage.py", "runserver", "0:8000"]
CMD ["gunicorn", "--bind", "foodgram.wsgi:application", "0:8000" ]