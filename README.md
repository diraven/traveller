# Traveler

A simplistic discord bot developed for select Ukrainian discord communities.

Runs as an HTTP interactions endpoint on Cloudflare Workers: Discord posts every slash command to the worker, there is no gateway connection and no server to keep alive. State lives in D1, Cloudflare's managed SQLite. Layout follows Discord's [cloudflare-sample-app](https://github.com/discord/cloudflare-sample-app): `src/commands.ts` (definitions), `src/register.ts` (registration), `src/server.ts` (routing), `src/handlers/` (one file per command), `src/db.ts` and `migrations/` (persistence), `test/` (Vitest running inside workerd).

Commands: `/faq`, `/slap`, `/rusni_pyzda`, `/verify`, `/verification`, `/bans_sharing`, plus a "Поширити бан" entry in a user's right-click "Apps" menu. The dictionary commands were dropped: sum.in.ua is unreachable and sum20ua.com put a captcha in front of its API.

Ban detection differs from the gateway version: instead of watching the audit log, a moderator bans as usual and then shares the ban explicitly with `/bans_sharing share` or the right-click entry.

# Development

```sh
npm install
cp .dev.vars.example .dev.vars
vi .dev.vars                     # application id, public key, bot token from the Developer Portal
npm run db:migrate               # apply migrations to the local database
npm test                         # unit tests
npm run typecheck && npm run lint
DISCORD_DEV_GUILD_ID=<id> npm run register   # register commands into one server instantly
npm run register                 # or globally (propagates within an hour)
npm start                        # local server on http://localhost:8787
```

# Database

D1, with plain SQL migrations in `migrations/`. Snowflakes are stored as TEXT: they exceed 2^53 and JavaScript numbers would corrupt them.

```sh
npx wrangler d1 migrations create traveller <name>   # new migration
npm run db:migrate                                   # apply locally
npm run db:migrate:remote                            # apply to production
```

Point Discord at a local server by exposing it through a tunnel (for example `cloudflared tunnel --url http://localhost:8787`) and using that URL as the Interactions Endpoint URL.

Commit hooks: `pre-commit install --install-hooks && pre-commit install --install-hooks -t commit-msg`. Releases: `cz bump`, then publish the GitHub release; delivery deploys the worker and registers commands.

# Deployment

```sh
npx wrangler login
npx wrangler d1 create traveller   # paste the id it prints into wrangler.jsonc
npm run db:migrate:remote
npx wrangler secret put DISCORD_APPLICATION_ID
npx wrangler secret put DISCORD_PUBLIC_KEY
npx wrangler secret put DISCORD_TOKEN
npm run deploy
```

Then set the worker URL as "Interactions Endpoint URL" on the application's General Information page in the Developer Portal. Discord sends a PING to validate the endpoint, which the worker answers, and from then on interactions arrive over HTTPS.

Continuous delivery needs these repository secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `DISCORD_APPLICATION_ID`, `DISCORD_TOKEN`.

# Шаринг банів між серверами

Бот розташований на мережі українських серверів та може повідомляти вам про бан якщо на іншому сервері когось забанили.

Для підключення до сповіщень про бани треба:

- Запросити бота на свій сервер: https://discord.com/oauth2/authorize?client_id=966727208586584135&permissions=84096&scope=bot%20applications.commands
- Налаштувати канал сповіщень за допомогою `/bans_sharing set_channel`.
- Перевірити що все налаштовано правильно за допомогою `/bans_sharing check_config`.

Щоб поширити бан: забаньте користувача як завжди, а потім скористайтеся командою `/bans_sharing share` або натисніть на користувача правою кнопкою і оберіть "Apps" → "Поширити бан".

## ЧаПи

### Режими

Бот може працювати в двох режимах:

1. Якщо у бота є право на бан - повідомлення про бани будуть інтерактивні та матимуть кнопки "забанити" та "проігнорувати".
2. Якщо у бота немає права на бан - він просто буде постити повідомлення з командою бану яку треба буде скопіпастити у віконце введення повідомлення.

### Як оформити бан?

Баньте як зручно, а потім поширте бан командою `/bans_sharing share`. Повідомлення про бан надійде на інші сервери підключені до системи. Постарайтесь чітко вказати причину бану з посиланнями на скріншоти. Тоді шанси що ваш бан також застосують на інших серверах значно вищі.

### Кому можна довіряти?

Довірений модератор (`/bans_sharing add_trusted_moderator`) отримує право банити на вашому сервері без вашого підтвердження. Бот перевіряє, що бан справді існує на сервері-джерелі, перш ніж поширювати його, але саме рішення про бан лишається за тим модератором. Додавайте в довірені лише тих, кому справді довіряєте.

### Це безпечно?

В режимі без права на бан - так. Ніяких прав у бота крім як дивитися аудит лог, постити повідомлення в визначений канал і створювати слеш-команди нема. Тому використовувати його безпечно. Найгірше що може статися - бот запостить повідомлення сумнівного контенту в канали в який ви йому дозволили писати.

В режимі коли у бота є право на бан - ви фактично даєте право бану власнику бота, тобто мені. Чи варта зручність натискання кнопки замість копіювання команди такого ризику - вирішувати вам.

### Мені заважають інші слеш-команди бота. Як їх прибрати?

Discord дозволяє забрати доступ до використання окремих слеш-команд по ролях. Користуйтеся.

### А може краще окремого бота конкретно під цю задачу?

В ідеалі, так. Треба зробити окремого бота який не робитиме нічого крім повідомлення про бани. Можливо, колись. Або ні.
