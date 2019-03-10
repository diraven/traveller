FROM python:3.7
WORKDIR /app
ENTRYPOINT ["./docker-entrypoint"]
CMD ["python", "main.py"]

RUN apt-get update && apt-get install wait-for-it -y

COPY Pipfile.lock Pipfile ./
RUN pip install --upgrade pip pipenv && pipenv install --system --dev

COPY . .
