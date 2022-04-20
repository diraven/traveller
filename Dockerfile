FROM python:3.10
LABEL maintainer="oleksa.pavlenko@gmail.com"
WORKDIR /app/

# OS dependencoes.
RUN apt update && apt install -y docker.io zsh

# Python dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --requirement requirements.txt

# Project files.
COPY . .
ENV FLASK_APP=crabot/main.py
CMD ["gunicorn", "--bind", "0.0.0.0:80", "crabot.main:app"]
