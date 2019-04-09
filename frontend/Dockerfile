FROM python:3.7
WORKDIR /app

ENTRYPOINT ["./docker-entrypoint"]
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:80", "--workers", "3"]
COPY docker-entrypoint .

ENV PIPENV_VENV_IN_PROJECT=1
COPY Pipfile Pipfile.lock ./
RUN apt-get update && apt-get install wait-for-it -y
RUN pip install --upgrade pip pipenv && pipenv sync

COPY . .
