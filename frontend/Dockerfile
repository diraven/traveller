FROM python:3.7
WORKDIR /app

COPY docker-entrypoint /usr/bin/docker-entrypoint
ENTRYPOINT ["docker-entrypoint"]
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:80", "--workers", "3"]

RUN apt-get update && apt-get install wait-for-it -y
RUN pip install --upgrade pip pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY . .
