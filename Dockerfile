FROM python:3.9
LABEL maintainer="oleksa.pavlenko@gmail.com"
WORKDIR /app/

# OS dependencoes.
RUN apt update && apt install -y docker.io zsh && \
    sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Python dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --requirement requirements.txt

# Project files.
COPY . .
ENV FLASK_APP=crabot/main.py
CMD ["gunicorn", "crabot.main:app"]
