-- The Python bot filled created_at in from the application side, so the
-- production columns are NOT NULL with no usable default: trusted moderators
-- have none at all, and bans_sharing_bans has a literal timestamp frozen at the
-- moment the 2023 migration ran. Let the database stamp both.

ALTER TABLE bans_sharing_bans
  ALTER COLUMN created_at SET DEFAULT now();

ALTER TABLE bans_sharing_trusted_moderators
  ALTER COLUMN created_at SET DEFAULT now();
