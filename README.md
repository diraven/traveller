# Traveler

A simplistic discord both developed for select Ukrainian discord communitites.

# Development

- pre-commit install --install-hooks
- pre-commit install --install-hooks -t commit-msg
- `docker compose up --detach db` - starting db without bot
- `source .env && PGPASSWORD=$POSTGRES_PASSWORD psql --user postgres postgres` - connecting to local db

# DB Migrations

- `alembic revision --autogenerate` - generate new migration
- `alembic upgrade head` - run migrations

# Setup

```sh
uv venv
uv pip install -r requirements.txt --strict
cp example.env .env
vi .env # add your credentials
touch .data.sqlite
docker compose build
docker compose up -d
```

# Шаринг банів між серверами

Бот розташований на мережі українських серверів та може повідомляти вам про бан якщо на іншому сервері когось забанили.

Для підключення до сповіщень про бани треба:

- Запросити бота на свій сервер: https://discord.com/oauth2/authorize?client_id=966727208586584135&permissions=84096&scope=bot%20applications.commands
- Налаштувати канал сповіщень за допомогою `/bans_sharing set_channel`.
- Перевірити що все налаштовано правильно за допомогою `/bans_sharing check_config`.

## ЧаПи

### Режими

Бот може працювати в двох режимах:

1. Якщо у бота є право на бан - повідомлення про бани будуть інтерактивні та матимуть кнопки "забанити" та "проігнорувати".
2. Якщо у бота немає права на бан - він просто буде постити повідомлення з командою бану яку треба буде скопіпастити у віконце введення повідомлення.

### Як оформити бан?

Баньте як зручно. Повідомлення про бан надійде на інші сервери підключені до системи. Постарайтесь чітко вказати причину бану з посиланнями на скріншоти. Тоді шанси що ваш бан також застосують на інших серверах значно вищі.

### Це безпечно?

В режимі без права на бан - так. Ніяких прав у бота крім як дивитися аудит лог, постити повідомлення в визначений канал і створювати слеш-команди нема. Тому використовувати його безпечно. Найгірше що може статися - бот запостить повідомлення сумнівного контенту в канали в який ви йому дозволили писати.

В режимі коли у бота є право на бан - ви фактично даєте право бану власнику бота, тобто мені. Чи варта зручність натискання кнопки замість копіювання команди такого ризику - вирішувати вам.

### Мені заважають інші слеш-команди бота. Як їх прибрати?

Discord дозволяє забрати доступ до використання окремих слеш-команд по ролях. Користуйтеся.

### А може краще окремого бота конкретно під цю задачу?

В ідеалі, так. Треба зробити окремого бота який не робитиме нічого крім повідомлення про бани. Можливо, колись. Або ні.
