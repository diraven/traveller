# Privacy Policy

**Application:** Traveler (Подорожній) Discord bot
**Last updated:** 2026-08-13

This policy explains what data the Traveler Discord bot ("the bot") collects,
why it collects it, how long it is kept, and how to request its deletion.

## Data we store

The bot stores only the minimum data required for its features. All stored data
consists of Discord identifiers and configuration — **no message content, no
presence data, and no personal profile data** beyond what is listed below.

| Data | Purpose |
| --- | --- |
| Server (guild) IDs and names | Identify the servers the bot operates in and their configuration. |
| Notification-channel IDs | Know where to post ban-sharing notifications. |
| Verification-role IDs | Know which role to grant during peer verification. |
| Trusted-moderator user IDs and global usernames | Apply the "trusted moderator" ban-sharing feature. |
| Shared-ban records: banned user ID, ban reason, acting moderator ID, timestamp | Notify connected servers about bans and prevent duplicate notifications. |

The bot does **not** use the Message Content or Presence intents. It operates
entirely through slash commands and does not read message content or track user
presence.

## Where data is stored

Data is stored in a self-hosted PostgreSQL database on infrastructure controlled
by the bot owner. The underlying storage volume is encrypted at rest.

## Data retention

- **Server, channel, role, and trusted-moderator records** are kept for as long
  as the bot is a member of the server. When the bot is removed from a server,
  that server's configuration records are deleted.
- **Shared-ban records** are retained to prevent duplicate cross-server ban
  notifications. They can be deleted on request (see below).

## Requesting deletion

You can request deletion of your data by contacting the bot owner via our
Discord server: **https://discord.gg/NpeAj5A**

Upon request, the relevant records (for example, trusted-moderator entries or
shared-ban records associated with you) will be removed from the database.

## Changes to this policy

This policy may be updated over time. The "Last updated" date at the top of this
document reflects the most recent revision.
