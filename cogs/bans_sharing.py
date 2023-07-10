import logging
import typing as t

import discord
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from discord.ext import commands

import models

logger = logging.getLogger("mod")


async def setup(bot: commands.Bot) -> None:
    class BansSharingCog(commands.Cog):
        root_command = discord.app_commands.Group(
            name="mod",
            description="Модерація",
            guild_ids=[guild.id for guild in bot.guilds],
        )

        def __init__(self) -> None:
            self._bot = bot
            super().__init__()

        @commands.Cog.listener()
        async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry) -> None:
            if entry.action != discord.AuditLogAction.ban:
                return
            if not entry.target:
                return

            actor = t.cast(discord.Member, entry.user)
            target = await bot.fetch_user(int(entry.target.id))
            guild = entry.guild

            if actor is None or target is None:
                logger.warning(
                    "Audit log entry: %s - missing actor or target.", entry.id
                )
                return

            logger.info("Ban event: %s - received.", target.id)
            with sa_orm.Session(models.engine) as session, session.begin():
                # Before doing anything else - make sure we did not see this ban already.
                try:
                    session.execute(
                        sa.select(models.KnownBan).filter(
                            models.KnownBan.id == target.id
                        )
                    ).one()
                    logger.info("Ban event: %s - already seen, skipped.", target.id)
                    return
                except sa_orm.exc.NoResultFound:  # type: ignore
                    pass

                # Get channels we'll be sending notifications into.
                # Getting all that are set except for originating server.
                log_channels_ids = session.execute(
                    sa.select(models.Guild.log_channel_id).filter(
                        models.Guild.log_channel_id.is_not(None),
                        models.Guild.id != guild.id,
                    )
                )
                # And turn them into discord objects.
                log_channels = [
                    t.cast(discord.TextChannel, bot.get_channel(channel_id))
                    for (channel_id,) in log_channels_ids
                ]

                # Create embed and populate it with data.
                embed = discord.Embed(
                    title="Новий бан",
                )
                embed.add_field(name="Сервер", value=f"{guild.name} ({guild.id})")
                embed.add_field(
                    name="Модератор",
                    value=f"{actor.display_name} '{actor.name}' ({actor.id})",
                )
                embed.add_field(
                    name="Забанений",
                    value=f"{target.mention} '{target.name}' ({target.id})",
                )
                embed.add_field(name="Причина бану", value=entry.reason)
                if target.avatar:
                    embed.set_thumbnail(url=target.avatar.url)
                embed.set_footer(
                    text="Для створення такого самого бану на "
                    "цьому сервері - скопіюйте та "
                    "відправте текстову команду нижче."
                )

                # For each logging channel:
                for log_channel in log_channels:
                    try:
                        msg = await log_channel.send(
                            embed=embed,
                        )
                        reason = f" reason:{entry.reason}"
                        # We have to leave "delete_messages" parameter below empty since it's
                        # value depends on the language of the discord interface and will
                        # give errors on language mismatch.
                        # Post the message.
                        await msg.reply(
                            f"/ban user:{target.id} delete_messages:{reason if entry.reason else ''}",
                            suppress_embeds=True,
                        )
                    except discord.errors.Forbidden:
                        logger.warning(
                            "Cannot send message to %s (%s).",
                            log_channel.name,
                            log_channel.guild.name,
                        )

                # Mark ban as seen.
                logger.info(
                    "Ban event: %s - is new, marking as seen.",
                    target.id,
                )
                session.add(models.KnownBan(id=target.id, reason=entry.reason))

    await bot.add_cog(BansSharingCog())
