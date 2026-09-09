/**
 * Error reporting. Imported first from `index.ts` so Sentry is initialised
 * before anything it instruments. Without a DSN everything here is a no-op and
 * errors only reach the container logs.
 */
import process from "node:process";
import * as Sentry from "@sentry/node";

import { config } from "./config.ts";

if (config.sentryDsn) {
	Sentry.init({
		dsn: config.sentryDsn,
		...(config.release && { release: config.release }),
	});
}

/** Logs an error and, when Sentry is configured, reports it. */
export function captureError(error: unknown): void {
	console.error(error);
	if (config.sentryDsn) {
		Sentry.captureException(error);
	}
}

/**
 * Reports an error the process cannot continue past, then exits non-zero so the
 * container is restarted. Staying up in an unknown state is worse: the bot
 * looks healthy and answers nothing.
 */
export async function captureFatal(error: unknown): Promise<never> {
	captureError(error);
	if (config.sentryDsn) {
		// Give the report a moment to leave before the process goes away.
		await Sentry.close(2000).catch(() => undefined);
	}
	process.exit(1);
}
