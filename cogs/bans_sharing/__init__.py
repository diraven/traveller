import logging
import typing as t

import discord
import sqlalchemy as sa
from discord.ext import commands

import models

from . import confirm_share

logger = logging.getLogger("mod")


class BansSharingCog(models.Cog):
    root_command = discord.app_commands.Group(
        name="bans_sharing",
        description="Шаринг банів",
    )

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry) -> None:
        if entry.user is None or entry.target is None:
            raise RuntimeError(
                f"Audit log entry: {entry.id} - missing actor or target."
            )
        ban_guild = entry.guild
        ban_actor = t.cast(discord.Member, entry.user)
        ban_target = self.bot.get_user(
            int(entry.target.id)
        ) or await self.bot.fetch_user(int(entry.target.id))
        ban_reason = entry.reason or ""

        with models.Session.begin() as session:
            await confirm_share.process(
                bot=self.bot,
                session=session,
                ban_guild=ban_guild,
                ban_actor=ban_actor,
                ban_target=ban_target,
                ban_reason=ban_reason,
            )

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
        with models.Session.begin() as session:
            guild = session.execute(
                sa.select(models.Guild).filter_by(id_=interaction.guild_id)
            ).scalar_one()
            guild.bans_sharing_channel_id = channel.id

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
        with models.Session.begin() as session:
            guild: models.Guild = session.execute(
                sa.select(models.Guild).filter_by(id_=interaction.guild_id)
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
            color=discord.Color.green() if len(problems) == 0 else discord.Color.red(),
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
    ) -> None:
        if not interaction.guild:
            return
        guild = interaction.guild

        # Try to find ban entry.
        ban_entry: t.Optional[discord.AuditLogEntry] = None
        async for entry in guild.audit_logs(limit=1):
            if (
                entry.user
                and entry.user.id == interaction.user.id
                and entry.action == discord.AuditLogAction.ban
            ):
                ban_entry = entry

        # Process entry or post response.
        if ban_entry:
            if ban_entry.user is None or ban_entry.target is None:
                raise RuntimeError(
                    f"Audit log entry: {ban_entry.id} - missing actor or target."
                )
            guild = ban_entry.guild
            actor = t.cast(discord.Member, ban_entry.user)
            target = self.bot.get_user(
                int(ban_entry.target.id)
            ) or await self.bot.fetch_user(int(ban_entry.target.id))
            reason = ban_entry.reason or ""

            with models.Session.begin() as session:
                await confirm_share.process(
                    session=session,
                    bot=self.bot,
                    ban_guild=guild,
                    ban_actor=actor,
                    ban_target=target,
                    ban_reason=reason,
                )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Підходящий запис в лозі не знайдено",
                    description="",
                    color=discord.Color.red(),
                ),
            )
