FROM python:3.9
LABEL maintainer="oleksa.pavlenko@gmail.com"
WORKDIR /app/

# OS dependencoes.
RUN apt update && apt install -y docker.io

# Python dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --requirement requirements.txt

# Project files.
COPY . .
ENV FLASK_APP=main.py
CMD ["gunicorn", "main:app"]
