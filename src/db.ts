/**
 * Postgres access. Snowflakes live in bigint columns and node-postgres returns
 * bigint as a string, which is what the rest of the code wants: they exceed
 * 2^53 and would be corrupted by JavaScript numbers.
 *
 * Column names come from the schema the Python bot left behind, so the primary
 * keys are `id_`; queries alias them to something readable.
 */
import type { Pool } from "pg";

/** Anything that can run a query: a pool, a client, or a test double. */
export type Queryable = Pick<Pool, "query">;

export interface GuildRow {
	id: string;
	bans_sharing_channel_id: string | null;
	verification_role_id: string | null;
}

export interface TrustedModeratorRow {
	guild_id: string;
	user_id: string;
	user_global_name: string;
	created_by: string;
	created_at: Date;
}

export interface BansSharingChannel {
	guild_id: string;
	channel_id: string;
}

export async function getGuild(
	db: Queryable,
	guildId: string,
): Promise<GuildRow | null> {
	const { rows } = await db.query<GuildRow>(
		`SELECT id_ AS id, bans_sharing_channel_id, verification_role_id
     FROM guilds WHERE id_ = $1`,
		[guildId],
	);
	return rows[0] ?? null;
}

export async function setBansSharingChannel(
	db: Queryable,
	guildId: string,
	channelId: string,
): Promise<void> {
	await db.query(
		`INSERT INTO guilds (id_, bans_sharing_channel_id) VALUES ($1, $2)
     ON CONFLICT (id_) DO UPDATE SET bans_sharing_channel_id = EXCLUDED.bans_sharing_channel_id`,
		[guildId, channelId],
	);
}

export async function setVerificationRole(
	db: Queryable,
	guildId: string,
	roleId: string,
): Promise<void> {
	await db.query(
		`INSERT INTO guilds (id_, verification_role_id) VALUES ($1, $2)
     ON CONFLICT (id_) DO UPDATE SET verification_role_id = EXCLUDED.verification_role_id`,
		[guildId, roleId],
	);
}

/** Every guild with bans sharing configured, except `excludeGuildId`. */
export async function listBansSharingChannels(
	db: Queryable,
	excludeGuildId: string,
): Promise<BansSharingChannel[]> {
	const { rows } = await db.query<BansSharingChannel>(
		`SELECT id_ AS guild_id, bans_sharing_channel_id AS channel_id FROM guilds
     WHERE bans_sharing_channel_id IS NOT NULL AND id_ <> $1
     ORDER BY id_`,
		[excludeGuildId],
	);
	return rows;
}

// Guild bookkeeping. The gateway tells us when the bot joins or leaves, and
// PRIVACY.md promises a server's records go away when it removes the bot.

export async function upsertGuild(
	db: Queryable,
	guildId: string,
	name: string,
): Promise<void> {
	await db.query(
		`INSERT INTO guilds (id_, name) VALUES ($1, $2)
     ON CONFLICT (id_) DO UPDATE SET name = EXCLUDED.name`,
		[guildId, name],
	);
}

export async function deleteGuild(
	db: Queryable,
	guildId: string,
): Promise<void> {
	await db.query(
		"DELETE FROM bans_sharing_trusted_moderators WHERE guild_id = $1",
		[guildId],
	);
	await db.query("DELETE FROM guilds WHERE id_ = $1", [guildId]);
}

export async function listGuildIds(db: Queryable): Promise<string[]> {
	const { rows } = await db.query<{ id: string }>(
		"SELECT id_ AS id FROM guilds",
	);
	return rows.map((row) => row.id);
}

// Trusted moderators.

/** Returns false when the moderator is already trusted on that guild. */
export async function addTrustedModerator(
	db: Queryable,
	row: Omit<TrustedModeratorRow, "created_at">,
): Promise<boolean> {
	// id_ is a surrogate bigserial, and created_at defaults to now(); only the
	// unique constraint on (guild_id, user_id) matters here.
	const result = await db.query(
		`INSERT INTO bans_sharing_trusted_moderators
       (created_by, guild_id, user_id, user_global_name)
     VALUES ($1, $2, $3, $4)
     ON CONFLICT (guild_id, user_id) DO NOTHING`,
		[row.created_by, row.guild_id, row.user_id, row.user_global_name],
	);
	return (result.rowCount ?? 0) > 0;
}

/** Returns the removed row, or null when there was nothing to remove. */
export async function removeTrustedModerator(
	db: Queryable,
	guildId: string,
	userId: string,
): Promise<TrustedModeratorRow | null> {
	const { rows } = await db.query<TrustedModeratorRow>(
		`DELETE FROM bans_sharing_trusted_moderators
     WHERE guild_id = $1 AND user_id = $2
     RETURNING guild_id, user_id, user_global_name, created_by, created_at`,
		[guildId, userId],
	);
	return rows[0] ?? null;
}

export async function listTrustedModerators(
	db: Queryable,
	guildId: string,
): Promise<TrustedModeratorRow[]> {
	const { rows } = await db.query<TrustedModeratorRow>(
		`SELECT guild_id, user_id, user_global_name, created_by, created_at
     FROM bans_sharing_trusted_moderators
     WHERE guild_id = $1 ORDER BY created_at, user_id`,
		[guildId],
	);
	return rows;
}

export async function isTrustedModerator(
	db: Queryable,
	guildId: string,
	userId: string,
): Promise<boolean> {
	const { rowCount } = await db.query(
		`SELECT 1 FROM bans_sharing_trusted_moderators
     WHERE guild_id = $1 AND user_id = $2`,
		[guildId, userId],
	);
	return (rowCount ?? 0) > 0;
}

// Seen bans, so the same ban is never shared twice.

export async function hasSeenBan(
	db: Queryable,
	userId: string,
): Promise<boolean> {
	const { rowCount } = await db.query(
		"SELECT 1 FROM bans_sharing_bans WHERE id_ = $1",
		[userId],
	);
	return (rowCount ?? 0) > 0;
}

export async function recordBan(
	db: Queryable,
	userId: string,
	createdBy: string,
	reason: string | undefined,
): Promise<void> {
	// id_ here is the banned user's snowflake, which is what makes the table
	// deduplicate by user.
	await db.query(
		`INSERT INTO bans_sharing_bans (id_, reason, created_by)
     VALUES ($1, $2, $3)
     ON CONFLICT (id_) DO NOTHING`,
		[userId, reason ?? null, createdBy],
	);
}
