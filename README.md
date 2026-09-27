# Traveler

A simplistic discord bot developed for select Ukrainian discord communities.

Runs as a gateway client on a VPS, deployed with Coolify. State lives in Postgres. Layout: `src/index.ts` (client and event routing), `src/commands.ts` (definitions, registered on connect), `src/handlers/` (one file or directory per command), `src/db.ts` and `migrations/` (persistence), `test/` (Vitest).

Node runs the TypeScript sources directly by stripping types, so there is no build step and no compiler in the runtime image.

Commands: `/faq`, `/slap`, `/rusni_pyzda`, `/verify`, `/verification`, `/bans_sharing`, plus a "Поширити бан" entry in a user's right-click "Apps" menu. The dictionary commands were dropped: sum.in.ua is unreachable and sum20ua.com put a captcha in front of its API.

# Development

```sh
pnpm install
docker compose up -d              # Postgres on localhost:5432
cp .env.example .env
vi .env                           # bot token from the Developer Portal
pnpm db:migrate                   # optional, the bot also migrates on startup
pnpm typecheck && pnpm lint
pnpm test                         # unit tests; database tests need TEST_DATABASE_URL
pnpm start                        # registers commands globally; reload Discord to see changes
```

Database tests run only when pointed at a throwaway database, and they truncate every table - so point them somewhere other than the development database above:

```sh
docker run --rm -e POSTGRES_PASSWORD=test -e POSTGRES_DB=traveller_test -p 55432:5432 postgres:18-alpine
TEST_DATABASE_URL=postgres://postgres:test@localhost:55432/traveller_test pnpm test
```

Commit hooks install themselves with `pnpm install` (lefthook). Releases: publish a GitHub release, which triggers the deployment.

# Database

Plain SQL migrations in `migrations/`, applied in filename order and recorded in `schema_migrations`. The bot applies pending migrations at startup, so a deploy needs no separate step.

Snowflakes live in `bigint` columns. node-postgres returns `bigint` as a string, which is what the code wants: they exceed 2^53 and JavaScript numbers would corrupt them. Note that `id_` means different things per table - the guild snowflake in `guilds`, the banned user's snowflake in `bans_sharing_bans`, and a surrogate `bigserial` in `bans_sharing_trusted_moderators`.

# Deployment

A published release builds `ghcr.io/diraven/traveller` (tagged with the version and `latest`) and triggers a redeploy of the Coolify service that runs it. The service needs:

- A Postgres service, with `DATABASE_URL` pointing at it, or the standard `PGHOST`/`PGUSER`/`PGPASSWORD`/`PGDATABASE` variables.
- `DISCORD_TOKEN` (or `DISCORD_BOT_TOKEN`) from the Developer Portal.
- Optionally `SENTRY_DSN` for error reporting, and `RELEASE` to tag it.

No privileged gateway intents are needed: the bot uses Guilds and Guild Moderation. It does need the **View Audit Log** permission on each server, which is how it notices bans.

Continuous delivery needs a `COOLIFY_TOKEN` secret in the `production` environment: a Coolify API token with the deploy ability. It restarts the service with `latest=true`, since Coolify's deploy webhook does not pull a newer image under the same tag.

# Шаринг банів між серверами

Бот розташований на мережі українських серверів та може повідомляти вам про бан якщо на іншому сервері когось забанили.

Для підключення до сповіщень про бани треба:

- Запросити бота на свій сервер: https://discord.com/oauth2/authorize?client_id=966727208586584135&permissions=84096&scope=bot%20applications.commands
- Налаштувати канал сповіщень за допомогою `/bans_sharing set_channel`.
- Перевірити що все налаштовано правильно за допомогою `/bans_sharing check_config`.

Бот сам помічає бани в аудит лозі і питає у вашому каналі сповіщень, чи поширювати бан на інші сервери. Якщо бан стався коли бот був недоступний - скористайтеся командою `/bans_sharing share` або натисніть на користувача правою кнопкою і оберіть "Apps" → "Поширити бан".

Кожен бан опрацьовується один раз на всю мережу серверів. Якщо ви натиснули "Не поширювати" або пропустили запит - поширити той самий бан пізніше вже не вийде.

## ЧаПи

### Режими

Бот може працювати в двох режимах:

1. Якщо у бота є право на бан - повідомлення про бани будуть інтерактивні та матимуть кнопки "забанити" та "проігнорувати".
2. Якщо у бота немає права на бан - він просто буде постити повідомлення з командою бану яку треба буде скопіпастити у віконце введення повідомлення.

### Як оформити бан?

Баньте як зручно - бот сам запитає, чи поширювати бан. Повідомлення про бан надійде на інші сервери підключені до системи. Постарайтесь чітко вказати причину бану з посиланнями на скріншоти. Тоді шанси що ваш бан також застосують на інших серверах значно вищі.

### Кому можна довіряти?

Довірений модератор (`/bans_sharing add_trusted_moderator <ідентифікатор>`) отримує право банити на вашому сервері без вашого підтвердження. Саме рішення про бан лишається за тим модератором. Додавайте в довірені лише тих, кому справді довіряєте.

### Це безпечно?

В режимі без права на бан - так. Ніяких прав у бота крім як дивитися аудит лог, постити повідомлення в визначений канал і створювати слеш-команди нема. Тому використовувати його безпечно. Найгірше що може статися - бот запостить повідомлення сумнівного контенту в канали в який ви йому дозволили писати.

В режимі коли у бота є право на бан - ви фактично даєте право бану власнику бота, тобто мені. Чи варта зручність натискання кнопки замість копіювання команди такого ризику - вирішувати вам.

### Мені заважають інші слеш-команди бота. Як їх прибрати?

Discord дозволяє забрати доступ до використання окремих слеш-команд по ролях. Користуйтеся.

### А може краще окремого бота конкретно під цю задачу?

В ідеалі, так. Треба зробити окремого бота який не робитиме нічого крім повідомлення про бани. Можливо, колись. Або ні.
