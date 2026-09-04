/**
 * Worker bindings. Secrets are set with `wrangler secret put <NAME>` in
 * production and read from `.dev.vars` by `wrangler dev`; the D1 database
 * comes from `wrangler.jsonc`.
 *
 * Declared as an augmentation of `Cloudflare.Env` so `env` imported from
 * `cloudflare:workers` and `cloudflare:test` carries the same type.
 */
declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace Cloudflare {
    interface Env {
      /**
       * Also the bot's user id: Discord has issued the two as the same
       * snowflake for every app for years, and the code relies on that when
       * it looks the bot up as a guild member.
       */
      DISCORD_APPLICATION_ID: string;
      DISCORD_PUBLIC_KEY: string;
      DISCORD_TOKEN: string;
      DB: D1Database;
    }
  }
}

export type Env = Cloudflare.Env;
