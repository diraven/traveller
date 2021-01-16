FROM python:3.9
LABEL maintainer="oleksa.pavlenko@gmail.com"
WORKDIR /app/

RUN apt update && apt upgrade -y && apt install -y docker docker-compose

COPY docker-entrypoint /usr/bin/docker-entrypoint
ENTRYPOINT ["docker-entrypoint"]

COPY . .
RUN pip install --requirement requirements.txt

CMD ["python", "main.py"]
