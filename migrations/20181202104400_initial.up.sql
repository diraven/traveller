BEGIN TRANSACTION;

CREATE TABLE django_migrations
(
  id      SERIAL                   NOT NULL
    CONSTRAINT django_migrations_pkey
    PRIMARY KEY,
  app     VARCHAR(255)             NOT NULL,
  name    VARCHAR(255)             NOT NULL,
  applied TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE django_content_type
(
  id        SERIAL       NOT NULL
    CONSTRAINT django_content_type_pkey
    PRIMARY KEY,
  app_label VARCHAR(100) NOT NULL,
  model     VARCHAR(100) NOT NULL,
  CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq
  UNIQUE (app_label, model)
);

CREATE TABLE auth_permission
(
  id              SERIAL       NOT NULL
    CONSTRAINT auth_permission_pkey
    PRIMARY KEY,
  name            VARCHAR(255) NOT NULL,
  content_type_id INTEGER      NOT NULL
    CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co
    REFERENCES django_content_type
      DEFERRABLE INITIALLY DEFERRED,
  codename        VARCHAR(100) NOT NULL,
  CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq
  UNIQUE (content_type_id, codename)
);

CREATE INDEX auth_permission_content_type_id_2f476e4b
  ON auth_permission (content_type_id);

CREATE TABLE auth_group
(
  id   SERIAL      NOT NULL
    CONSTRAINT auth_group_pkey
    PRIMARY KEY,
  name VARCHAR(80) NOT NULL
    CONSTRAINT auth_group_name_key
    UNIQUE
);

CREATE INDEX auth_group_name_a6ea08ec_like
  ON auth_group (name);

CREATE TABLE auth_group_permissions
(
  id            SERIAL  NOT NULL
    CONSTRAINT auth_group_permissions_pkey
    PRIMARY KEY,
  group_id      INTEGER NOT NULL
    CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id
    REFERENCES auth_group
      DEFERRABLE INITIALLY DEFERRED,
  permission_id INTEGER NOT NULL
    CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm
    REFERENCES auth_permission
      DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq
  UNIQUE (group_id, permission_id)
);

CREATE INDEX auth_group_permissions_group_id_b120cbf9
  ON auth_group_permissions (group_id);

CREATE INDEX auth_group_permissions_permission_id_84c5c92e
  ON auth_group_permissions (permission_id);

CREATE TABLE auth_user
(
  id           SERIAL                   NOT NULL
    CONSTRAINT auth_user_pkey
    PRIMARY KEY,
  password     VARCHAR(128)             NOT NULL,
  last_login   TIMESTAMP WITH TIME ZONE,
  is_superuser BOOLEAN                  NOT NULL,
  username     VARCHAR(150)             NOT NULL
    CONSTRAINT auth_user_username_key
    UNIQUE,
  first_name   VARCHAR(30)              NOT NULL,
  last_name    VARCHAR(150)             NOT NULL,
  email        VARCHAR(254)             NOT NULL,
  is_staff     BOOLEAN                  NOT NULL,
  is_active    BOOLEAN                  NOT NULL,
  date_joined  TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX auth_user_username_6821ab7c_like
  ON auth_user (username);

CREATE TABLE auth_user_groups
(
  id       SERIAL  NOT NULL
    CONSTRAINT auth_user_groups_pkey
    PRIMARY KEY,
  user_id  INTEGER NOT NULL
    CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id
    REFERENCES auth_user
      DEFERRABLE INITIALLY DEFERRED,
  group_id INTEGER NOT NULL
    CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id
    REFERENCES auth_group
      DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq
  UNIQUE (user_id, group_id)
);

CREATE INDEX auth_user_groups_user_id_6a12ed8b
  ON auth_user_groups (user_id);

CREATE INDEX auth_user_groups_group_id_97559544
  ON auth_user_groups (group_id);

CREATE TABLE auth_user_user_permissions
(
  id            SERIAL  NOT NULL
    CONSTRAINT auth_user_user_permissions_pkey
    PRIMARY KEY,
  user_id       INTEGER NOT NULL
    CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id
    REFERENCES auth_user
      DEFERRABLE INITIALLY DEFERRED,
  permission_id INTEGER NOT NULL
    CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm
    REFERENCES auth_permission
      DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq
  UNIQUE (user_id, permission_id)
);

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b
  ON auth_user_user_permissions (user_id);

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c
  ON auth_user_user_permissions (permission_id);

CREATE TABLE django_admin_log
(
  id              SERIAL                   NOT NULL
    CONSTRAINT django_admin_log_pkey
    PRIMARY KEY,
  action_time     TIMESTAMP WITH TIME ZONE NOT NULL,
  object_id       TEXT,
  object_repr     VARCHAR(200)             NOT NULL,
  action_flag     smallint                 NOT NULL
    CONSTRAINT django_admin_log_action_flag_check
    check (action_flag >= 0),
  change_message  TEXT                     NOT NULL,
  content_type_id INTEGER
    CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co
    REFERENCES django_content_type
      DEFERRABLE INITIALLY DEFERRED,
  user_id         INTEGER                  NOT NULL
    CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id
    REFERENCES auth_user
      DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX django_admin_log_content_type_id_c4bce8eb
  ON django_admin_log (content_type_id);

CREATE INDEX django_admin_log_user_id_c564eba6
  ON django_admin_log (user_id);

CREATE TABLE mydiscord_guild
(
  id         SERIAL     NOT NULL
    CONSTRAINT mydiscord_guild_pkey
    PRIMARY KEY,
  discord_id TEXT       NOT NULL
    CONSTRAINT mydiscord_guild_uid_key
    UNIQUE,
  name       TEXT       NOT NULL
    CONSTRAINT mydiscord_guild_name_key
    UNIQUE,
  trigger    VARCHAR(1) NOT NULL
);

CREATE TABLE mydiscord_module
(
  id   SERIAL      NOT NULL
    CONSTRAINT mydiscord_module_pkey
    PRIMARY KEY,
  name VARCHAR(16) NOT NULL
    CONSTRAINT mydiscord_module_name_key
    UNIQUE
);

CREATE INDEX mydiscord_module_name_2ad38893_like
  ON mydiscord_module (name);

CREATE TABLE mydiscord_guild_modules
(
  id        SERIAL  NOT NULL
    CONSTRAINT mydiscord_guild_modules_pkey
    PRIMARY KEY,
  guild_id  INTEGER NOT NULL
    CONSTRAINT mydiscord_guild_modules_guild_id_df8d8bd2_fk_mydiscord_guild_id
    REFERENCES mydiscord_guild
      DEFERRABLE INITIALLY DEFERRED,
  module_id INTEGER NOT NULL
    CONSTRAINT mydiscord_guild_modu_module_id_cbe54763_fk_mydiscord
    REFERENCES mydiscord_module
      DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT mydiscord_guild_modules_guild_id_module_id_8ebde6b2_uniq
  UNIQUE (guild_id, module_id)
);

CREATE INDEX mydiscord_guild_modules_guild_id_df8d8bd2
  ON mydiscord_guild_modules (guild_id);

CREATE INDEX mydiscord_guild_modules_module_id_cbe54763
  ON mydiscord_guild_modules (module_id);

CREATE TABLE mydiscord_alias
(
  id       SERIAL      NOT NULL
    CONSTRAINT mydiscord_alias_pkey
    PRIMARY KEY,
  source   VARCHAR(16) NOT NULL,
  target   VARCHAR(64) NOT NULL,
  guild_id INTEGER     NOT NULL
    CONSTRAINT mydiscord_alias_guild_id_74af358c_fk_mydiscord_guild_id
    REFERENCES mydiscord_guild
      DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT mydiscord_alias_guild_id_source_87623941_uniq
  UNIQUE (guild_id, source)
);

CREATE INDEX mydiscord_alias_guild_id_74af358c
  ON mydiscord_alias (guild_id);

CREATE TABLE publicroles_publicrole
(
  id         SERIAL  NOT NULL
    CONSTRAINT publicroles_publicrole_pkey
    PRIMARY KEY,
  discord_id TEXT    NOT NULL
    CONSTRAINT publicroles_publicrole_uid_key
  UNIQUE,
  guild_id   INTEGER NOT NULL
    CONSTRAINT publicroles_publicrole_guild_id_84bbf8da_fk_mydiscord_guild_id
    REFERENCES mydiscord_guild
      DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX publicroles_publicrole_guild_id_84bbf8da
  ON publicroles_publicrole (guild_id);

CREATE TABLE django_session
(
  session_key  VARCHAR(40)              NOT NULL
    CONSTRAINT django_session_pkey
    PRIMARY KEY,
  session_data TEXT                     NOT NULL,
  expire_date  TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX django_session_session_key_c0390e0f_like
  ON django_session (session_key);

CREATE INDEX django_session_expire_date_a5c62663
  ON django_session (expire_date);

COMMIT;
