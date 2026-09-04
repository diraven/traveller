/**
 * D1 access. Snowflakes are stored as TEXT: they exceed 2^53 and would be
 * corrupted by JavaScript numbers.
 */

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
  created_at: string;
}

export interface BansSharingChannel {
  guild_id: string;
  channel_id: string;
}

export function getGuild(
  db: D1Database,
  guildId: string,
): Promise<GuildRow | null> {
  return db
    .prepare("SELECT * FROM guilds WHERE id = ?")
    .bind(guildId)
    .first<GuildRow>();
}

export async function setBansSharingChannel(
  db: D1Database,
  guildId: string,
  channelId: string,
): Promise<void> {
  await db
    .prepare(
      `INSERT INTO guilds (id, bans_sharing_channel_id) VALUES (?, ?)
       ON CONFLICT (id) DO UPDATE SET bans_sharing_channel_id = excluded.bans_sharing_channel_id`,
    )
    .bind(guildId, channelId)
    .run();
}

export async function setVerificationRole(
  db: D1Database,
  guildId: string,
  roleId: string,
): Promise<void> {
  await db
    .prepare(
      `INSERT INTO guilds (id, verification_role_id) VALUES (?, ?)
       ON CONFLICT (id) DO UPDATE SET verification_role_id = excluded.verification_role_id`,
    )
    .bind(guildId, roleId)
    .run();
}

/** Every guild with bans sharing configured, except `excludeGuildId`. */
export async function listBansSharingChannels(
  db: D1Database,
  excludeGuildId: string,
): Promise<BansSharingChannel[]> {
  const { results } = await db
    .prepare(
      `SELECT id AS guild_id, bans_sharing_channel_id AS channel_id FROM guilds
       WHERE bans_sharing_channel_id IS NOT NULL AND id != ?
       ORDER BY id`,
    )
    .bind(excludeGuildId)
    .run<BansSharingChannel>();
  return results;
}

/** Returns false when the moderator is already trusted on that guild. */
export async function addTrustedModerator(
  db: D1Database,
  row: Omit<TrustedModeratorRow, "created_at">,
): Promise<boolean> {
  const { meta } = await db
    .prepare(
      `INSERT OR IGNORE INTO bans_sharing_trusted_moderators
         (guild_id, user_id, user_global_name, created_by)
       VALUES (?, ?, ?, ?)`,
    )
    .bind(row.guild_id, row.user_id, row.user_global_name, row.created_by)
    .run();
  return meta.changes > 0;
}

/** Returns the removed row, or null when there was nothing to remove. */
export async function removeTrustedModerator(
  db: D1Database,
  guildId: string,
  userId: string,
): Promise<TrustedModeratorRow | null> {
  return db
    .prepare(
      `DELETE FROM bans_sharing_trusted_moderators
       WHERE guild_id = ? AND user_id = ? RETURNING *`,
    )
    .bind(guildId, userId)
    .first<TrustedModeratorRow>();
}

export async function listTrustedModerators(
  db: D1Database,
  guildId: string,
): Promise<TrustedModeratorRow[]> {
  const { results } = await db
    .prepare(
      `SELECT * FROM bans_sharing_trusted_moderators
       WHERE guild_id = ? ORDER BY created_at, user_id`,
    )
    .bind(guildId)
    .run<TrustedModeratorRow>();
  return results;
}

export async function isTrustedModerator(
  db: D1Database,
  guildId: string,
  userId: string,
): Promise<boolean> {
  const row = await db
    .prepare(
      `SELECT 1 FROM bans_sharing_trusted_moderators
       WHERE guild_id = ? AND user_id = ?`,
    )
    .bind(guildId, userId)
    .first();
  return row !== null;
}

export async function hasSeenBan(
  db: D1Database,
  userId: string,
): Promise<boolean> {
  const row = await db
    .prepare("SELECT 1 FROM bans_sharing_bans WHERE user_id = ?")
    .bind(userId)
    .first();
  return row !== null;
}

export async function recordBan(
  db: D1Database,
  userId: string,
  createdBy: string,
  reason: string | undefined,
): Promise<void> {
  await db
    .prepare(
      `INSERT OR IGNORE INTO bans_sharing_bans (user_id, reason, created_by)
       VALUES (?, ?, ?)`,
    )
    .bind(userId, reason ?? null, createdBy)
    .run();
}
