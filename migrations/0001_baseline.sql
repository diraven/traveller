-- The schema as the Python bot's alembic history left it. Snowflakes are
-- bigint; node-postgres returns bigint as a string, which is what the code
-- wants because snowflakes exceed 2^53.
--
-- IF NOT EXISTS throughout, so applying this to the existing production
-- database is a no-op and a fresh database gets the same shape.

CREATE TABLE IF NOT EXISTS guilds (
  id_ bigint PRIMARY KEY,
  name varchar(100),
  bans_sharing_channel_id bigint,
  verification_role_id bigint
);

CREATE TABLE IF NOT EXISTS bans_sharing_bans (
  id_ bigint PRIMARY KEY,
  reason varchar(500),
  created_at timestamptz NOT NULL DEFAULT now(),
  created_by bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS bans_sharing_trusted_moderators (
  id_ bigserial PRIMARY KEY,
  created_at timestamptz NOT NULL DEFAULT now(),
  created_by bigint NOT NULL,
  guild_id bigint NOT NULL,
  user_id bigint NOT NULL,
  user_global_name varchar(32) NOT NULL,
  CONSTRAINT uq_bans_sharing_trusted_moderators_guild_id UNIQUE (guild_id, user_id)
);
