import discord
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from discord.ext import commands

import models


async def setup(bot: commands.Bot) -> None:
    class ConfigurationCog(commands.Cog):
        root_command = discord.app_commands.Group(
            name="configure",
            description="Налаштування",
            guild_ids=[guild.id for guild in bot.guilds],
        )

        @root_command.command(description="Налаштувати канал сповіщень")  # type: ignore
        @discord.app_commands.guild_only()
        @discord.app_commands.checks.has_permissions(administrator=True)
        async def log_channel(
            self,
            interaction: discord.Interaction[commands.Bot],
            channel: discord.TextChannel,
        ) -> None:
            with sa_orm.Session(models.engine) as session:
                guild = session.execute(
                    sa.select(models.Guild).filter_by(id=interaction.guild_id)
                ).scalar_one()
                guild.log_channel_id = channel.id
                session.commit()

            embed = discord.Embed(
                title="Змінено канал сповіщень бота",
                description=f"Новий канал сповіщень: {channel.mention}",
            )
            await interaction.response.send_message(
                embed=embed,
            )

        def __init__(self) -> None:
            self._bot = bot
            super().__init__()

    await bot.add_cog(ConfigurationCog())
