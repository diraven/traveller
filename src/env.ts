/**
 * Worker bindings. Secrets are set with `wrangler secret put <NAME>` in
 * production and read from `.dev.vars` by `wrangler dev`.
 */
export interface Env {
  DISCORD_APPLICATION_ID: string;
  DISCORD_PUBLIC_KEY: string;
  DISCORD_TOKEN: string;
}
