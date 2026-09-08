/**
 * Configuration from the environment. In production Coolify injects these; for
 * local development a `.env` file next to the sources is loaded if present.
 */
import { existsSync } from "node:fs";
import process from "node:process";

if (existsSync(".env")) {
	process.loadEnvFile(".env");
}

function required(name: string): string {
	const value = process.env[name];
	if (!value) {
		throw new Error(`The ${name} environment variable is required.`);
	}
	return value;
}

export const config = {
	discordToken: required("DISCORD_TOKEN"),
	databaseUrl: required("DATABASE_URL"),
	/** Error reporting is optional; without a DSN errors only reach the logs. */
	sentryDsn: process.env.SENTRY_DSN,
	/**
	 * Registers commands into this one server instead of globally. Global
	 * registration can take up to an hour to propagate, a guild is instant.
	 */
	devGuildId: process.env.DISCORD_DEV_GUILD_ID,
	release: process.env.RELEASE,
} as const;
