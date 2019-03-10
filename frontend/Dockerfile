FROM python:3.6
WORKDIR /app
ENTRYPOINT ["./docker-entrypoint"]
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:80", "--workers", "3"]

RUN apt update && apt install wait-for-it -y

COPY Pipfile.lock Pipfile ./
RUN pip install --upgrade pip pipenv && pipenv install --system --dev

COPY . .
