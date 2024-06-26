import typing as t

import discord
import sqlalchemy as sa
from discord.ext import commands

import models


class VerificationCog(commands.Cog):
    root_command = discord.app_commands.Group(
        name="verification",
        description="Верифікація",
    )

    def __init__(self, bot: models.Bot) -> None:
        self.bot = bot
        super().__init__()

    @root_command.command(  # type: ignore
        description="Налаштувати роль верифікації",
    )
    @discord.app_commands.guild_only()
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def set_role(
        self,
        interaction: discord.Interaction[commands.Bot],
        role: discord.Role,
    ) -> None:
        # Save new role id.
        with models.Session.begin() as session:
            guild = session.execute(
                sa.select(models.Guild).filter_by(id_=interaction.guild_id)
            ).scalar_one()
            guild.verification_role_id = role.id

        # Send confirmation message.
        embed = discord.Embed(
            title="Змінено роль верифікації",
            description=f"Нова роль верифікації: {role.mention}",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(
            embed=embed,
        )

    @root_command.command(  # type: ignore
        description="Перевірити налаштування верифікації",
    )
    @discord.app_commands.guild_only()
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def check_config(
        self,
        interaction: discord.Interaction[commands.Bot],
    ) -> None:
        # Make sure command is used in guild.
        if not interaction.guild:
            return

        problems: list[tuple[str, str]] = []

        # Make sure bot has manage roles permission.
        permissions = interaction.guild.me.guild_permissions
        if not permissions.manage_roles:
            problems.append(
                (
                    "Відсутній дозвіл на управління ролями.",
                    "Надайте боту доступ до управління ролями.",
                )
            )

        # Make sure role is defined.
        with models.Session.begin() as session:
            guild: models.Guild = session.execute(
                sa.select(models.Guild).filter_by(id_=interaction.guild_id)
            ).scalar_one()
            if guild.verification_role_id:
                # Make sure role exists.
                role = t.cast(
                    discord.Role,
                    interaction.guild.get_role(guild.verification_role_id),
                )
                # Make sure we can give/revoke role specified.
                try:
                    await interaction.guild.me.add_roles(role)
                    await interaction.guild.me.remove_roles(role)
                except discord.errors.Forbidden:
                    problems.append(
                        (
                            f"Відсутній дозвіл для видачі ролі {role.mention}.",
                            "Перевірте щоб роль була розташована нижче ролі бота",
                        )
                    )
            else:
                problems.append(
                    (
                        "Роль верифікації не задана.",
                        "Вкажіть роль верифікації для бота за допомогою команди "
                        "`/verification set_role`.",
                    )
                )

        # Post check results.
        embed = discord.Embed(
            title="Результати перевірки налаштувань верифікації",
            description="Все ок." if len(problems) == 0 else "",
            color=discord.Color.green() if len(problems) == 0 else discord.Color.red(),
        )
        for problem, suggestion in problems:
            embed.add_field(name=problem, value=suggestion, inline=False)
        await interaction.response.send_message(
            embed=embed,
        )

    @discord.app_commands.command(  # type: ignore
        description="Верифікувати користувача",
    )
    @discord.app_commands.guild_only()
    async def verify(
        self,
        interaction: discord.Interaction[commands.Bot],
        member: discord.Member,
    ) -> None:
        # Make sure command is used in guild.
        if not interaction.guild:
            return

        actor = t.cast(
            discord.Member, interaction.guild.get_member(interaction.user.id)
        )
        target = member
        if not member:
            return

        if actor == member:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="???",
                    description="Самоверифікацією... кхм-кхм... "
                    "краще займатися деінде.",
                    color=discord.Color.red(),
                )
            )
            return

        if interaction.guild.me == member:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="???",
                    description="А мене за шо?)",
                    color=discord.Color.red(),
                )
            )
            return

        # Prepare error embed.
        error_embed = discord.Embed(
            title="Помилка",
            description="Скористайтесь командою `/verification check_config` "
            "(тільки для адміністраторів) для налаштування верифікації.",
            color=discord.Color.red(),
        )

        # Load verification role.
        with models.Session.begin() as session:
            guild: models.Guild = session.execute(
                sa.select(models.Guild).filter_by(id_=interaction.guild_id)
            ).scalar_one()
            if guild.verification_role_id:
                # Get the role.
                role = t.cast(
                    discord.Role,
                    interaction.guild.get_role(guild.verification_role_id),
                )

                # Make sure actor already has this role.
                if role not in actor.roles:
                    await interaction.response.send_message(
                        embed=discord.Embed(
                            title="Помилка",
                            description="Тільки верифіковані користувачі "
                            "можуть верифікувати інших.",
                            color=discord.Color.red(),
                        )
                    )
                    return

                # Make sure target does not have this role yet.
                if role in target.roles:
                    await interaction.response.send_message(
                        embed=discord.Embed(
                            title="Помилка",
                            description=f"Користувача {target.mention} "
                            "вже верифіковано.",
                            color=discord.Color.red(),
                        )
                    )
                    return

                # Assign the role.
                try:
                    await target.add_roles(
                        role, reason=f"{actor.mention} '{actor.name}' ({actor.id})"
                    )
                except discord.errors.Forbidden:
                    await interaction.response.send_message(embed=error_embed)
                    return
            else:
                await interaction.response.send_message(embed=error_embed)
                return

        # Send confirmation message.
        embed = discord.Embed(
            title="Верифікація",
            description=f"{actor.mention} верифікує {target.mention} "
            f"відкриваючи доступ до голосових каналів, "
            "постингу посилань, картинок та ін.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(
            embed=embed,
        )
