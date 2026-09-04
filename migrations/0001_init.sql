-- Snowflakes are TEXT: they exceed 2^53 and JavaScript numbers would corrupt them.

CREATE TABLE guilds (
  id TEXT PRIMARY KEY,
  bans_sharing_channel_id TEXT,
  verification_role_id TEXT
);

CREATE TABLE bans_sharing_trusted_moderators (
  guild_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  user_global_name TEXT NOT NULL,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  PRIMARY KEY (guild_id, user_id)
);

CREATE TABLE bans_sharing_bans (
  user_id TEXT PRIMARY KEY,
  reason TEXT,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
