/**
 * Gives every test a clean, migrated D1 database: `reset()` clears all
 * bindings, then the migrations recreate the schema.
 */
import type { D1Migration } from "@cloudflare/vitest-plugin";
import { applyD1Migrations, env, reset } from "cloudflare:test";
import { beforeEach } from "vitest";

const bindings = env as typeof env & { TEST_MIGRATIONS: D1Migration[] };

beforeEach(async () => {
  await reset();
  await applyD1Migrations(bindings.DB, bindings.TEST_MIGRATIONS);
});
