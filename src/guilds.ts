/**
 * Keeps the `guilds` table matching the servers the bot is actually in.
 *
 * PRIVACY.md promises a server's records go away when it removes the bot, so
 * this runs on join, on leave, and once at startup to catch anything that
 * happened while the bot was offline.
 */
import type { Client } from "discord.js";

import * as db from "./db.ts";

export async function reconcileGuilds(
	client: Client,
	queryable: db.Queryable,
): Promise<void> {
	const current = client.guilds.cache;

	for (const guild of current.values()) {
		// A guild in the middle of an outage is in the cache with no name yet;
		// storing that would blank the name we already have. It is not gone, so
		// the sweep below leaves its records alone either way.
		if (!guild.available) {
			continue;
		}
		await db.upsertGuild(queryable, guild.id, guild.name);
	}

	// Safe because the bot runs as a single unsharded process: at ready the
	// cache holds every guild it is in, so anything else really is gone.
	for (const storedId of await db.listGuildIds(queryable)) {
		if (!current.has(storedId)) {
			await db.deleteGuild(queryable, storedId);
		}
	}
}
