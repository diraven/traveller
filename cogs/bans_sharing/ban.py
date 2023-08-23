import logging
import typing as t

import discord
import sentry_sdk
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from discord.ext import commands

import models
import settings
import utils

from . import classes

logger = logging.getLogger()


class View(discord.ui.View):
    def __init__(self, *, bot: models.Bot, timeout: float | None = 180):
        self.message: t.Optional[discord.Message] = None
        self.bot = bot

        super().__init__(timeout=timeout)

    async def on_timeout(self) -> None:
        # Disable all controls.
        for item in self.children:
            item.disabled = True  # type: ignore
        if self.message:
            self.message.embeds[0].description = "**Статус:** проігноровано"
            await self.message.edit(embed=self.message.embeds[0], view=self)

    @discord.ui.button(label="Теж забанити", style=discord.ButtonStyle.red)
    async def ban(
        self,
        interaction: discord.Interaction[commands.Bot],
        button: discord.ui.Button["View"],
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
            self.message.embeds[
                0
            ].description = (
                f"**Статус:** теж забанено модератором {interaction.user.mention}."
            )

            data = classes.Fields.from_embed(self.message.embeds[0])

            # Perform ban itself.
            if interaction.guild:
                await interaction.guild.ban(
                    discord.Object(data.target_id), reason=data.reason
                )

            # Disable all the controls.
            for item in self.children:
                item.disabled = True  # type: ignore
            # Update message and it's view.
            await interaction.response.edit_message(
                embed=self.message.embeds[0], view=self
            )

    @discord.ui.button(label="Ігнорувати", style=discord.ButtonStyle.gray)
    @discord.app_commands.checks.has_permissions(ban_members=True)
    async def skip(
        self,
        interaction: discord.Interaction[commands.Bot],
        button: discord.ui.Button["View"],
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
            self.message.embeds[
                0
            ].description = (
                f"**Статус:** проігноровано модератором {interaction.user.mention}"
            )

            # Disable all the controls.
            for item in self.children:
                item.disabled = True  # type: ignore
            # Update message and it's view.
            await interaction.response.edit_message(
                embed=self.message.embeds[0], view=self
            )


async def process(
    *,
    bot: models.Bot,
    session: sa_orm.Session,
    ban_guild: discord.Guild,
    ban_actor: discord.User,
    ban_target: discord.User,
    ban_reason: t.Optional[str],
) -> None:
    logger.info("Ban event: %s - received.", ban_target.id)
    if not settings.DEBUG:
        # Get channels we'll be sending notifications into.
        # Getting all that are set except for originating server.
        log_channels_ids = session.execute(
            sa.select(models.Guild.bans_sharing_channel_id).filter(
                models.Guild.bans_sharing_channel_id.is_not(None),
                models.Guild.id_ != ban_guild.id,
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

    # Post ban embeds.
    for log_channel in log_channels:
        # Create embed and populate it with data.
        embed = await classes.Fields(
            guild_id=str(ban_guild.id),
            actor_id=str(ban_actor.id),
            target_id=str(ban_target.id),
            reason=ban_reason,
        ).to_embed(bot)
        embed.title = "Новий бан на іншому сервері"

        try:
            # Detect whether bot has ban permissions.
            if not bot.user:
                raise RuntimeError("Unable to fetch own user.")
            bot_member = log_channel.guild.get_member(bot.user.id)
            if not bot_member:
                raise RuntimeError("Unable to fetch own member.")
            can_ban = bot_member.guild_permissions.ban_members

            if can_ban:
                view = View(bot=bot, timeout=3600 * 24)
                view.message = await log_channel.send(
                    embed=embed,
                    view=view,
                )
            else:
                embed.set_footer(
                    text="У бота відсутні права на бан. "
                    "Для створення такого самого бану на "
                    "цьому сервері вам доведеться скопіювати та "
                    "відправити текстову команду нижче."
                )
                msg = await log_channel.send(
                    embed=embed,
                )
                # We have to leave "delete_messages" parameter below empty since
                # it's value depends on the language of the discord interface
                # and will give errors on language mismatch.
                # Post the message.
                cmd_reason = f" reason: {ban_reason}" if ban_reason else ""
                await msg.reply(
                    f"/ban user:{ban_target.id} " f"delete_messages:{cmd_reason}",
                    suppress_embeds=True,
                )
        except discord.errors.Forbidden as exc:
            sentry_sdk.capture_exception(exc)
