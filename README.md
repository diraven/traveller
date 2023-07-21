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
touch .data.sqlite
docker-compose build
docker-compose up -d
```

# Шаринг банів між серверами

Бот розташований на мережі українських серверів та може повідомляти вам про бан якщо на іншому сервері когось забанили.

Для підключення до сповіщень про бани треба:

- Запросити бота на свій сервер: https://discord.com/oauth2/authorize?client_id=966727208586584135&permissions=84096&scope=bot%20applications.commands
- Налаштувати канал сповіщень за допомогою `/bans_sharing set_channel`.
- Перевірити що все налаштовано правильно за допомогою `/bans_sharing check_config`.

## ЧаПи

### Як оформити бан?

Баньте як зручно. Повідомлення про бан надійде на інші сервери підключені до системи. Постарайтесь чітко вказати причину бану з посиланнями на скріншоти. Тоді шанси що ваш бан також застосують на інших серверах значно вищі.

### Це безпечно?

Так. Ніяких прав у бота крім як дивитися аудит лог, постити повідомлення в визначений канал і створювати слеш-команди нема. Тому використовувати його безпечно.

### Мені заважають інші слеш-команди бота. Як їх прибрати?

Діскорд дозволяє забрати доступ до використання окремих слеш-команд по ролях. Користуйтеся.

### А може краще окремого бота конкретно під цю задачу?

В ідеалі, так. Треба зробити окремого бота який не робитиме нічого крім повідомлення про бани. Можливо, колись. Або ні.
