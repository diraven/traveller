# Traveller

A simplistic discord both developed for select Ukrainian discord communitites.

# Development

- pre-commit install --install-hooks
- pre-commit install --install-hooks -t commit-msg

# DB Migrations

- `alembic revision --autogenerate` - generate new migration
- `alembic upgrade head` - run migrations

# Setup

```sh
cp example.env .env
vi .env # add your credentials
docker-compose build
docker-compose up -d
```
