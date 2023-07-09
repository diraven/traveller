import logging
import typing as t
from typing import Optional

import discord
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from discord.ext import commands

import models
import utils

logger = logging.getLogger("mod")

BANNED_ID_FIELD_NAME = "ID забаненого"
BAN_REASON_FIELD_NAME = "Причина бану"


class BanView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        self.message: Optional[discord.Message] = None
        super().__init__(timeout=timeout)

    async def on_timeout(self) -> None:
        # Disable all controls.
        for item in self.children:
            item.disabled = True  # type: ignore # pylint: disable=no-member
        # Update the message.
        if self.message:
            await self.message.edit(view=self)

    @discord.ui.button(label="Теж забанити", style=discord.ButtonStyle.red)
    async def ban(
        self,
        interaction: discord.Interaction[commands.Bot],
        button: discord.ui.Button["BanView"],  # pylint: disable=unused-argument
    ) -> None:
        if self.message:
            # Make sure only people with ban_members permission can do this.
            if not utils.has_permission_for_interaction(interaction, "ban_members"):
                embed = discord.Embed(
                    color=discord.Color.red(),
                    title="Помилка",
                    description="Відсутній доступ.",
                )
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True,
                )
                return

            # Add status field into the embed.
            self.message.embeds[0].add_field(
                name="Статус",
                value=f"Теж забанено модератором {interaction.user.mention}",
            )

            # Get banned id.
            banned_id = int(
                next(
                    field
                    for field in self.message.embeds[0].fields
                    if field.name == BANNED_ID_FIELD_NAME
                ).value
                or ""
            )
            # Get banned reason.
            banned_reason = next(
                field
                for field in self.message.embeds[0].fields
                if field.name == BAN_REASON_FIELD_NAME
            ).value

            # Perform ban itself.
            if interaction.guild:
                await interaction.guild.ban(
                    discord.Object(banned_id), reason=banned_reason
                )

            # Disable all the controls.
            for item in self.children:
                item.disabled = True  # type: ignore # pylint: disable=no-member
            # Update message and it's view.
            await interaction.response.edit_message(
                embed=self.message.embeds[0], view=self
            )

    @discord.ui.button(label="Ігнорувати", style=discord.ButtonStyle.gray)
    @discord.app_commands.checks.has_permissions(ban_members=True)
    async def skip(
        self,
        interaction: discord.Interaction[commands.Bot],
        button: discord.ui.Button["BanView"],  # pylint: disable=unused-argument
    ) -> None:
        if self.message:
            # Make sure only people with ban_members permission can do this.
            if not utils.has_permission_for_interaction(interaction, "ban_members"):
                embed = discord.Embed(
                    color=discord.Color.red(),
                    title="Помилка",
                    description="Відсутній доступ.",
                )
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True,
                )
                return

            # Add status field into the embed.
            self.message.embeds[0].add_field(
                name="Статус",
                value=f"Проігноровано модератором {interaction.user.mention}",
            )

            # Disable all the controls.
            for item in self.children:
                item.disabled = True  # type: ignore # pylint: disable=no-member
            # Update message and it's view.
            await interaction.response.edit_message(
                embed=self.message.embeds[0], view=self
            )


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
                            value=f"{log.user.mention} '{log.user.name}' ({log.user.id})",
                        )
                        embed.add_field(
                            name="Забанений",
                            value=f"{target.mention} '{target.name}' ({target.id})",
                        )
                        embed.add_field(name=BANNED_ID_FIELD_NAME, value=target.id)
                        embed.add_field(name=BAN_REASON_FIELD_NAME, value=log.reason)
                        embed.set_footer(text=log.created_at)

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
                                pass

                            ban_view = BanView()
                            ban_view.message = await t.cast(
                                discord.TextChannel, log_channel
                            ).send(
                                embed=embed,
                                view=ban_view,
                            )

                        # Mark ban as seen.
                        logger.info(
                            "Ban event: %s - is new, marking as seen.",
                            member.id,
                        )
                        session.add(models.KnownBan(id=member.id, reason=log.reason))
                        break

    await bot.add_cog(ModerationCog())
