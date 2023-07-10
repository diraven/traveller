import logging
import typing as t

import discord
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from discord.ext import commands

import models

logger = logging.getLogger("mod")


async def setup(bot: commands.Bot) -> None:
    class ModerationCog(commands.Cog):
        root_command = discord.app_commands.Group(
            name="mod",
            description="Модерація",
            guild_ids=[guild.id for guild in bot.guilds],
        )

        def __init__(self) -> None:
            self._bot = bot
            super().__init__()

        @commands.Cog.listener()
        async def on_member_ban(
            self, guild: discord.Guild, member: discord.Member
        ) -> None:
            logger.info("Ban event: %s - received.", member.id)
            with sa_orm.Session(models.engine) as session, session.begin():
                # Before doing anything else - make sure we did not see this ban already.
                try:
                    session.execute(
                        sa.select(models.KnownBan).filter(
                            models.KnownBan.id == member.id
                        )
                    ).one()
                    logger.info("Ban event: %s - already seen, skipped.", member.id)
                    return
                except sa_orm.exc.NoResultFound:  # type: ignore
                    pass

                # Get channels we'll be sending notifications into.
                # Getting all that are set except for originating server.
                log_channels_ids = session.execute(
                    sa.select(models.Guild.id, models.Guild.log_channel_id).filter(
                        models.Guild.log_channel_id.is_not(None),
                        models.Guild.id != guild.id,
                    )
                )

                # Get actual guild and channel objects for further use.
                log_channels = [
                    (
                        t.cast(discord.Guild, bot.get_guild(guild_id)),
                        bot.get_channel(channel_id),
                    )
                    for (guild_id, channel_id) in log_channels_ids
                ]

                # Scan last few audit logs to figure out ban details.
                async for log in guild.audit_logs(
                    limit=10, action=discord.AuditLogAction.ban
                ):
                    # If we found the audit log record with our ban.
                    if log.target == member and log.user:
                        # Create embed and populate it with data.
                        embed = discord.Embed(
                            title="Новий бан",
                        )
                        target = t.cast(discord.Member, log.target)
                        embed.add_field(
                            name="Сервер", value=f"{guild.name} ({guild.id})"
                        )
                        embed.add_field(
                            name="Модератор",
                            value=f"{log.user.display_name} '{log.user.name}' ({log.user.id})",
                        )
                        embed.add_field(
                            name="Забанений",
                            value=f"{target.mention} '{target.name}' ({target.id})",
                        )
                        embed.add_field(name="Причина бану", value=log.reason)
                        if target.avatar:
                            embed.set_thumbnail(url=target.avatar.url)
                        embed.set_footer(
                            text="Для створення такого самого бану на "
                            "цьому сервері - скопіюйте та "
                            "відправте текстову команду нижче."
                        )

                        # For each logging channel:
                        for log_guild, log_channel in log_channels:
                            # Before sending the notification itself - make sure ban does not
                            # already exist.
                            try:
                                await log_guild.fetch_ban(member)
                                logger.info(
                                    "Ban event: %s - already banned, skipped.",
                                    member.id,
                                )
                                continue
                            except discord.errors.NotFound:
                                # Ban not found, we can proceed with notification.
                                pass

                            msg = await t.cast(discord.TextChannel, log_channel).send(
                                embed=embed,
                            )
                            reason = f" reason:{log.reason}"
                            # We have to leave "delete_messages" parameter below empty since it's
                            # value depends on the language of the discord interface and will
                            # give errors on language mismatch.
                            await msg.reply(
                                f"/ban user:{target.id} delete_messages:{reason if log.reason else ''}"
                            )

                        # Mark ban as seen.
                        logger.info(
                            "Ban event: %s - is new, marking as seen.",
                            member.id,
                        )
                        session.add(models.KnownBan(id=member.id, reason=log.reason))
                        break

    await bot.add_cog(ModerationCog())
