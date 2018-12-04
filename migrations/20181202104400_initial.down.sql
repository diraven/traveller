BEGIN TRANSACTION;

DROP TABLE django_session;
DROP TABLE publicroles_publicrole;
DROP TABLE mydiscord_alias;
DROP TABLE mydiscord_guild_modules;
DROP TABLE mydiscord_module;
DROP TABLE mydiscord_guild;
DROP TABLE django_admin_log;
DROP TABLE auth_user_user_permissions;
DROP TABLE auth_user_groups;
DROP TABLE auth_user;
DROP TABLE auth_group_permissions;
DROP TABLE auth_group;
DROP TABLE auth_permission;
DROP TABLE django_content_type;
DROP TABLE django_migrations;

COMMIT;