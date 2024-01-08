import logging
import typing as t

import discord
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from discord.ext import commands

import models
import settings
import utils

from . import ban, classes

logger = logging.getLogger()


class View(discord.ui.View):
    def __init__(self, *, bot: models.Bot, timeout: float | None = 180):
        self.message: t.Optional[discord.Message] = None
        self.bot: models.Bot = bot
        super().__init__(timeout=timeout)

    async def on_timeout(self) -> None:
        # Disable all controls.
        for item in self.children:
            item.disabled = True  # type: ignore
        if self.message and not self.message.embeds[0].description:
            # Update the message.
            self.message.embeds[0].description = "**Статус:** проігноровано"
            await self.message.edit(embed=self.message.embeds[0], view=self)

    @discord.ui.button(label="Поширити на інші сервери", style=discord.ButtonStyle.red)  # type: ignore
    async def yes(
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
            self.message.embeds[0].description = (
                "**Статус:** поширено на інші сервери "
                f"модератором {interaction.user.mention}"
            )
            # Disable all the controls.
            for item in self.children:
                item.disabled = True  # type: ignore
            # Update message and it's view.
            await interaction.response.edit_message(
                embed=self.message.embeds[0], view=self
            )

            data = classes.Fields.from_embed(self.message.embeds[0])

            # Send bans.
            ban_guild = self.bot.get_guild(int(data.guild_id))
            ban_target = self.bot.get_user(
                int(data.target_id)
            ) or await self.bot.fetch_user(int(data.target_id))
            ban_actor = self.bot.get_user(
                int(data.actor_id)
            ) or await self.bot.fetch_user(int(data.actor_id))
            if not interaction.guild:
                raise RuntimeError("Interaction has no guild.")
            if not ban_guild:
                raise RuntimeError("Ban has no guild!")
            if not ban_target:
                raise RuntimeError("Ban has no target!")
            if not ban_actor:
                raise RuntimeError("Ban has no actor!")

            with models.Session.begin() as session:
                await ban.process(
                    bot=self.bot,
                    session=session,
                    ban_guild=ban_guild,
                    ban_actor=ban_actor,
                    ban_target=ban_target,
                    ban_reason=data.reason,
                )

    @discord.ui.button(label="Не поширювати", style=discord.ButtonStyle.gray)  # type: ignore
    @discord.app_commands.checks.has_permissions(ban_members=True)
    async def no(
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
    ban_actor: discord.Member,
    ban_target: discord.User,
    ban_reason: t.Optional[str],
) -> None:
    logger.info("Ban event: %s - received.", ban_target.id)
    # Before doing anything else,
    # make sure we did not see this ban already.
    try:
        session.execute(
            sa.select(models.KnownBan).filter(models.KnownBan.id_ == ban_target.id)
        ).one()
        if not settings.DEBUG:
            logger.info("Ban event: %s - already seen, skipped.", ban_target.id)
            return
    except sa_orm.exc.NoResultFound:  # type: ignore
        pass

    # Get guild ban log channel id.
    bans_sharing_channel_id = bot.get_guild_config(
        session, ban_guild.id
    ).bans_sharing_channel_id
    if not bans_sharing_channel_id:
        # Bans sharing is not configured, skip everything else.
        # Make sure we don't mark ban as seen in this case as
        # other servers may still want to ban user and share
        # the ban.
        return

    # Mark ban as seen.
    if not settings.DEBUG:
        logger.info(
            "Ban event: %s - is new, marking as seen.",
            ban_target.id,
        )
        session.add(models.KnownBan(id_=ban_target.id, reason=ban_reason))

    # Get log channel.
    log_channel = t.cast(
        discord.TextChannel,
        bot.get_channel(bans_sharing_channel_id),
    )
    if not log_channel:
        raise RuntimeError(f"Unable to retrieve log channnel {bans_sharing_channel_id}")

    # Post confirmation embed before sending bans further.
    view = View(bot=bot, timeout=3600 * 24)
    embed = await classes.Fields(
        guild_id=str(ban_guild.id),
        actor_id=str(ban_actor.id),
        target_id=str(ban_target.id),
        reason=ban_reason,
    ).to_embed(bot)
    embed.title = "Новий бан на цьому сервері"
    embed.set_footer(text="Для застосування бану вручну, скористайтеся командою нижче.")
    view.message = await log_channel.send(
        content=utils.get_embed_field(embed, classes.BANNED_FIELD_NAME).value,
        embed=embed,
        view=view,
    )
    # We have to leave "delete_messages" parameter below empty since
    # it's value depends on the language of the discord interface
    # and will give errors on language mismatch.
    # Post the message.
    cmd_reason = f" reason: {ban_reason}" if ban_reason else ""
    await view.message.reply(
        f"/ban user:{ban_target.id} " f"delete_messages:{cmd_reason}",
        suppress_embeds=True,
    )
