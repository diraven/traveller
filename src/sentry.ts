/**
 * Error reporting. Imported first from `index.ts` so Sentry is initialised
 * before anything it instruments. Without a DSN everything here is a no-op and
 * errors only reach the container logs.
 */
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
