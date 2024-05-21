import discord
from discord.ext import commands


def get_embed_field(
    embed: discord.Embed, field_name: str
) -> "discord.embeds._EmbedFieldProxy":  # type: ignore
    return next(field for field in embed.fields if field.name == field_name)


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
