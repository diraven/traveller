import logging
import typing as t

import discord
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from discord.ext import commands

import models

from . import audit_log_ban_processor

logger = logging.getLogger("mod")


async def setup(bot: commands.Bot) -> None:
    class BansSharingCog(commands.Cog):
        root_command = discord.app_commands.Group(
            name="bans_sharing",
            description="Шаринг банів",
        )

        def __init__(self) -> None:
            self._bot = bot
            super().__init__()

        @commands.Cog.listener()
        async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry) -> None:
            await audit_log_ban_processor.process(bot, entry)

        @root_command.command(description="Налаштувати канал сповіщень")  # type: ignore
        @discord.app_commands.guild_only()
        @discord.app_commands.checks.has_permissions(administrator=True)
        async def set_channel(
            self,
            interaction: discord.Interaction[commands.Bot],
            channel: discord.TextChannel,
        ) -> None:
            # Make sure we can access specified channel.
            try:
                await channel.send(
                    embed=discord.Embed(
                        title="Перевірка",
                        description="Тестове повідомлення для перевірки "
                        f"доступу до каналу сповіщень {channel.mention}.",
                    )
                )
            except discord.errors.Forbidden:
                embed = discord.Embed(
                    title="Відсутній доступ",
                    description=(
                        "Відсутній доступ до каналу "
                        f"сповіщень {channel.mention}, "
                        "перевірте налаштування ролей."
                    ),
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
                guild.bans_sharing_channel_id = channel.id
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

        @root_command.command(  # type: ignore
            description="Перевірити налаштування шарингу банів",
        )
        @discord.app_commands.guild_only()
        @discord.app_commands.checks.has_permissions(administrator=True)
        async def check_config(
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
                if guild.bans_sharing_channel_id:
                    # Make sure bot is able to post into the log channel.
                    channel = t.cast(
                        discord.TextChannel,
                        interaction.guild.get_channel(guild.bans_sharing_channel_id),
                    )
                    try:
                        msg = await channel.send(
                            embed=discord.Embed(
                                title="Перевірка",
                                description="Тестове повідомлення-вставка (embed).",
                            )
                        )
                        await msg.reply(content="Тестове текстове повідомлення.")
                    except discord.errors.Forbidden as exc:
                        problems.append(
                            (
                                "Не вдалося відправити повідомлення "
                                f"в канал {channel.mention}.",
                                str(exc),
                            )
                        )
                else:
                    # Log channel is not defined.
                    problems.append(
                        (
                            "Не налаштовано канал сповіщень.",
                            "Налаштуйте канал сповіщень за допомогою команди "
                            "`/config log_channel`",
                        )
                    )

            # Post check results.
            embed = discord.Embed(
                title="Результати перевірки налаштувань шарингу банів",
                description="Все ок."
                if len(problems) == 0
                else """Помилка. Необхідні наступні права для каналу сповіщень:
* View Channel
* Send Messages
* Read Messages History
* Embed Links""",
                color=discord.Color.green()
                if len(problems) == 0
                else discord.Color.red(),
            )
            for problem, suggestion in problems:
                embed.add_field(name=problem, value=suggestion, inline=False)
            await interaction.response.send_message(
                embed=embed,
            )

        @root_command.command(  # type: ignore
            description="Обробити останній бан користувача",
        )
        @discord.app_commands.guild_only()
        @discord.app_commands.checks.has_permissions(administrator=True)
        async def debug(
            self,
            interaction: discord.Interaction[commands.Bot],
            moderator: discord.Member,
        ) -> None:
            if not interaction.guild:
                return
            guild = interaction.guild

            # Try to find ban entry.
            ban_entry: t.Optional[discord.AuditLogEntry] = None
            async for entry in guild.audit_logs():
                if (
                    entry.user
                    and entry.user.id == moderator.id
                    and entry.action == discord.AuditLogAction.ban
                ):
                    ban_entry = entry

            # Process entry or post response.
            if ban_entry:
                await audit_log_ban_processor.process(bot, ban_entry, debug=True)
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Підходящий запис в лозі не знайдено",
                        description="",
                        color=discord.Color.red(),
                    ),
                )

    await bot.add_cog(BansSharingCog())
