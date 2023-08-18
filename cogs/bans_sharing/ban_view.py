import typing as t

import discord
from discord.ext import commands

import utils

BANNED_ID_FIELD_NAME = "ID забаненого"
BAN_REASON_FIELD_NAME = "Причина бану"


class BanView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        self.message: t.Optional[discord.Message] = None
        super().__init__(timeout=timeout)

    async def on_timeout(self) -> None:
        # Disable all controls.
        for item in self.children:
            item.disabled = True  # type: ignore
        # Update message and it's view.
        if self.message:
            self.message.embeds[0].add_field(
                name="Статус",
                value="Проігноровано.",
            )
        # Update the message.
        if self.message:
            await self.message.edit(embed=self.message.embeds[0], view=self)

    @discord.ui.button(label="Теж забанити", style=discord.ButtonStyle.red)
    async def ban(
        self,
        interaction: discord.Interaction[commands.Bot],
        button: discord.ui.Button["BanView"],
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
                value=f"Теж забанено модератором {interaction.user.mention}.",
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
        button: discord.ui.Button["BanView"],
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
                item.disabled = True  # type: ignore
            # Update message and it's view.
            await interaction.response.edit_message(
                embed=self.message.embeds[0], view=self
            )
