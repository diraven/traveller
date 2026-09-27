/**
 * Configuration from the environment. In production Coolify injects these; for
 * local development a `.env` file next to the sources is loaded if present.
 */
import { existsSync } from "node:fs";
import process from "node:process";

if (existsSync(".env")) {
	process.loadEnvFile(".env");
}

/** The first of `names` that is set, so a variable can have a legacy alias. */
function required(...names: string[]): string {
	for (const name of names) {
		const value = process.env[name];
		if (value) {
			return value;
		}
	}
	throw new Error(
		`The ${names.join(" or ")} environment variable is required.`,
	);
}

export const config = {
	// DISCORD_BOT_TOKEN is what the Python bot's deployment still supplies.
	discordToken: required("DISCORD_TOKEN", "DISCORD_BOT_TOKEN"),
	/**
	 * Without it node-postgres falls back to the standard PGHOST, PGUSER,
	 * PGPASSWORD and PGDATABASE variables, which the Coolify service sets.
	 */
	databaseUrl: process.env.DATABASE_URL,
	/** Error reporting is optional; without a DSN errors only reach the logs. */
	sentryDsn: process.env.SENTRY_DSN,
	/**
	 * Registers commands into this one server instead of globally. Global
	 * registration can take up to an hour to propagate, a guild is instant.
	 */
	devGuildId: process.env.DISCORD_DEV_GUILD_ID,
	release: process.env.RELEASE,
} as const;
