FROM python:3.6
WORKDIR /app
COPY Pipfile.lock Pipfile ./

RUN apt update && apt install wait-for-it -y
RUN pip install --upgrade pip pipenv && pipenv install --system --dev

COPY . .

CMD ["bash"]