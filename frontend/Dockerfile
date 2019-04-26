FROM python:3.7
WORKDIR /app

ENTRYPOINT ["docker-entrypoint"]
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:80", "--workers", "3"]
COPY docker-entrypoint /usr/bin/

RUN apt-get update && apt-get install wait-for-it -y

COPY Pipfile Pipfile.lock ./
RUN pip install --upgrade pip pipenv && pipenv install --system --deploy

COPY . .
