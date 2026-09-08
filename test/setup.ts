/**
 * Nothing in the handlers reads configuration, but anything that transitively
 * imports `src/config.ts` would throw without these.
 */
import process from "node:process";

process.env.DISCORD_TOKEN ??= "test-token";
process.env.DATABASE_URL ??= "postgres://localhost/traveller_test";
