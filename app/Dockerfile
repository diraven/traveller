FROM python:3.7-alpine
LABEL maintainer="oleksa.pavlenko@gmail.com"
WORKDIR /app

COPY requirements.frozen.txt /opt/
RUN apk update && \
    apk add --no-cache --virtual .build-deps gcc musl-dev && \
    pip install --upgrade pip && \
    cd /opt/ && \
    pip install --no-cache-dir --requirement requirements.frozen.txt && \
    apk del .build-deps
RUN apk add bash

COPY docker-entrypoint /usr/bin/docker-entrypoint
COPY wait-for /usr/bin/wait-for
ENTRYPOINT ["docker-entrypoint"]
CMD ["python", "main.py"]

COPY . .
