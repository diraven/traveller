import typing as t

import discord
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from discord.ext import commands

import models


async def setup(bot: commands.Bot) -> None:
    class ConfigurationCog(commands.Cog):
        root_command = discord.app_commands.Group(
            name="config",
            description="Налаштування",
            guild_ids=[guild.id for guild in bot.guilds],
        )

        def __init__(self) -> None:
            self._bot = bot
            super().__init__()

        @root_command.command(description="Налаштувати канал сповіщень")  # type: ignore
        @discord.app_commands.guild_only()
        @discord.app_commands.checks.has_permissions(administrator=True)
        async def log_channel(
            self,
            interaction: discord.Interaction[commands.Bot],
            channel: discord.TextChannel,
        ) -> None:
            # Make sure we can access specified channel.
            try:
                await channel.send(
                    f"Тестове повідомлення для перевірки доступу до каналу сповіщень {channel.mention}."
                )
            except discord.errors.Forbidden:
                embed = discord.Embed(
                    title="Відсутній доступ",
                    description=f"Відсутній доступ до каналу сповіщень {channel.mention}, "
                    "перевірте налаштування ролей.",
                    color=discord.Color.red(),
                )
                await interaction.response.send_message(
                    embed=embed,
                )
                return

            # Save new log channel id.
            with sa_orm.Session(models.engine) as session:
                guild = session.execute(
                    sa.select(models.Guild).filter_by(id=interaction.guild_id)
                ).scalar_one()
                guild.log_channel_id = channel.id
                session.commit()

            # Send confirmation message.
            embed = discord.Embed(
                title="Змінено канал сповіщень бота",
                description=f"Новий канал сповіщень: {channel.mention}",
                color=discord.Color.green(),
            )

            await interaction.response.send_message(
                embed=embed,
            )

        @root_command.command(description="Перевірити налаштування")  # type: ignore
        @discord.app_commands.guild_only()
        @discord.app_commands.checks.has_permissions(administrator=True)
        async def check(
            self,
            interaction: discord.Interaction[commands.Bot],
        ) -> None:
            if not interaction.guild:
                return

            problems = []

            # Check Audit Log access.
            permissions = interaction.guild.me.guild_permissions
            if not permissions.view_audit_log:
                problems.append(
                    (
                        "Відсутній дозвіл на перегляд Audit Log.",
                        "Надайте боту доступ до Audit Log.",
                    )
                )

            # Check if bot is able to post into the log channel.
            with sa_orm.Session(models.engine) as session:
                guild: models.Guild = session.execute(
                    sa.select(models.Guild).filter_by(id=interaction.guild_id)
                ).scalar_one()
                if guild.log_channel_id:
                    # Make sure bot is able to post into the log channel.
                    channel = t.cast(
                        discord.TextChannel, bot.get_channel(guild.log_channel_id)
                    )
                    try:
                        await channel.send(
                            f"Тестове повідомлення для перевірки доступу до каналу сповіщень {channel.mention}."
                        )
                    except discord.errors.Forbidden:
                        problems.append(
                            (
                                f"Відсутній дозвіл для відправки повідомлень в канал сповіщень {channel.mention}.",
                                "Перевірте налаштування доступу до каналу сповіщень для бота.",
                            )
                        )
                else:
                    # Log channel is not defined.
                    problems.append(
                        (
                            "Не налаштовано канал сповіщень.",
                            "Налаштуйте канал сповіщень за допомогою команди `/config log_channel`",
                        )
                    )

            # Post check results.
            embed = discord.Embed(
                title="Результати перевірки налаштувань",
                description="Все ок." if len(problems) == 0 else "",
                color=discord.Color.green()
                if len(problems) == 0
                else discord.Color.red(),
            )
            for problem, suggestion in problems:
                embed.add_field(name=problem, value=suggestion, inline=False)
            await interaction.response.send_message(
                embed=embed,
            )

    await bot.add_cog(ConfigurationCog())
