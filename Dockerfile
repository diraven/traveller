FROM python:3.11

WORKDIR /app
RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN python -m poetry config virtualenvs.in-project true && \
    poetry install --only main

COPY . .

ENTRYPOINT ["/app/entrypoint.sh"]
CMD [".venv/bin/python", "./main.py"]
