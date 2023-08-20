import logging
import typing as t

import discord
import sentry_sdk
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from discord.ext import commands

import models

from . import ban_view

logger = logging.getLogger()


async def process(
    bot: commands.Bot, entry: discord.AuditLogEntry, debug: bool = False
) -> None:
    if entry.action != discord.AuditLogAction.ban:
        return
    if not entry.target:
        return

    actor = t.cast(discord.Member, entry.user)
    target = await bot.fetch_user(int(entry.target.id))
    guild = entry.guild

    if actor is None or target is None:
        raise RuntimeError(f"Audit log entry: {entry.id} - missing actor or target.")

    logger.info("Ban event: %s - received.", target.id)
    with sa_orm.Session(models.engine) as session, session.begin():
        # Before doing anything else,
        # make sure we did not see this ban already.
        try:
            session.execute(
                sa.select(models.KnownBan).filter(models.KnownBan.id == target.id)
            ).one()
            if not debug:
                logger.info("Ban event: %s - already seen, skipped.", target.id)
                return
        except sa_orm.exc.NoResultFound:  # type: ignore
            pass

        if not debug:
            # Get channels we'll be sending notifications into.
            # Getting all that are set except for originating server.
            log_channels_ids = session.execute(
                sa.select(models.Guild.bans_sharing_channel_id).filter(
                    models.Guild.bans_sharing_channel_id.is_not(None),
                    models.Guild.id != guild.id,
                )
            )
        else:
            # Get all channels including originating one.
            log_channels_ids = session.execute(
                sa.select(models.Guild.bans_sharing_channel_id).filter(
                    models.Guild.bans_sharing_channel_id.is_not(None),
                )
            )
        # And turn them into discord objects.
        log_channels = [
            t.cast(discord.TextChannel, bot.get_channel(channel_id))
            for (channel_id,) in log_channels_ids
        ]

        await _post_embed(
            bot,
            guild,
            actor,
            target,
            entry.reason,
            log_channels,
        )

        # Mark ban as seen.
        if not debug:
            logger.info(
                "Ban event: %s - is new, marking as seen.",
                target.id,
            )
            session.add(models.KnownBan(id=target.id, reason=entry.reason))


async def _post_embed(
    bot: commands.Bot,
    guild: discord.Guild,
    actor: discord.Member,
    target: discord.User,
    reason: t.Optional[str],
    log_channels: t.List[discord.TextChannel],
) -> None:
    # Create embed and populate it with data.
    embed = discord.Embed(
        title=f"Бан на сервері {guild.name}",
    )
    embed.add_field(name="Сервер", value=f"{guild.name} ({guild.id})")
    embed.add_field(
        name="Модератор",
        value=f"{actor.display_name} '{actor.name}' ({actor.id})",
    )
    embed.add_field(
        name="Забанений",
        value=(
            f"{target.mention} '{target.display_name}' '{target.name}' "
            f"({target.id})"
        ),
    )
    embed.add_field(name=ban_view.BANNED_ID_FIELD_NAME, value=target.id)
    embed.add_field(name=ban_view.BAN_REASON_FIELD_NAME, value=reason)
    if target.avatar:
        embed.set_thumbnail(url=target.avatar.url)

    # For each logging channel:
    reason = f" reason: {reason}"
    for log_channel in log_channels:
        try:
            # Detect whether bot has ban permissions.
            if not bot.user:
                raise RuntimeError("Unable to fetch own user.")
            bot_member = log_channel.guild.get_member(bot.user.id)
            if not bot_member:
                raise RuntimeError("Unable to fetch own member.")
            can_ban = bot_member.guild_permissions.ban_members

            if can_ban:
                view = ban_view.BanView(timeout=3600)
                view.message = await log_channel.send(
                    embed=embed,
                    view=view,
                )
            else:
                embed.set_footer(
                    text="Для створення такого самого бану на "
                    "цьому сервері - скопіюйте та "
                    "відправте текстову команду нижче."
                )
                msg = await log_channel.send(
                    embed=embed,
                )
                # We have to leave "delete_messages" parameter below empty since
                # it's value depends on the language of the discord interface
                # and will give errors on language mismatch.
                # Post the message.
                await msg.reply(
                    f"/ban user:{target.id} "
                    f"delete_messages: {reason if reason else ''}",
                    suppress_embeds=True,
                )
        except discord.errors.Forbidden as exc:
            sentry_sdk.capture_exception(exc)
