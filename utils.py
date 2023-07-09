import discord
from discord.ext import commands


def has_permission_for_interaction(
    interaction: discord.Interaction[commands.Bot],
    permission: str,
) -> bool:
    # Get guild from interaction.
    if not interaction.guild:
        raise commands.NoPrivateMessage()

    # Get member from guild.
    member = interaction.guild.get_member(interaction.user.id)
    if not member:
        raise commands.UserNotFound(str(interaction.user.id))

    # Check permissions.
    return getattr(member.guild_permissions, permission)  # type: ignore
