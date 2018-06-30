from typing import List, Optional

from discord import Role, Forbidden
from discord.ext import commands
from django.utils.text import slugify

from mydiscord.cogbase import CogBase
from mydiscord.context import Context
from mydiscord.message import Message
from mydiscord.models import Guild
from publicroles.models import PublicRole


def sync_roles(ctx: Context) -> None:
    """
    Synchronizes locally stored list of roles with the real server roles.
    """

    # Get a list of stored public roles uids.
    public_role_uids = PublicRole.objects.filter(
        guild__uid=ctx.guild.id,
    ).values_list('uid', flat=True)

    # Get a list of real roles of the server.
    real_roles = {}
    for discord_role in ctx.guild.roles:
        real_roles[discord_role.id] = discord_role

    # Delete all roles we have stored locally that do not exist on the server
    # any more.
    for uid in public_role_uids:
        if uid not in real_roles.keys():
            PublicRole.objects.get(uid=uid).delete()


def find_public_roles(ctx: Context, term: Optional[str]) -> List[Role]:
    """
    Searches for a role in the public roles list and returns the result.
    """
    if not term:
        term = ""

    # Get a list of stored public roles uids.
    public_role_uids = PublicRole.objects.filter(
        guild__uid=ctx.guild.id,
    ).values_list('uid', flat=True)

    # Now search guild roles list for the term provided.
    roles_found = []
    for role in ctx.guild.roles:
        if role.id in public_role_uids and term.lower() in role.name.lower():
            roles_found.append(role)

    return roles_found


def format_roles(roles: List[Role]) -> str:
    """
    Converts discord roles list to the string representation. Limited to 1000
    symbols.
    """
    if roles:
        names = []
        length = 0
        for role in roles:
            length += len(role.name)
            if length > 1000:
                break
            names.append(role.name)
        return ", ".join(['`{}`'.format(name) for name in names])
    else:
        return "No roles found."


class Cog(CogBase):
    @commands.group(invoke_without_command=True)
    async def publicroles(
            self,
            ctx: Context,
            arg: str = ""
    ) -> None:
        sync_roles(ctx)

        roles = find_public_roles(ctx, arg)
        await ctx.post(Message(format_roles(roles), title="Public Roles"))

    @publicroles.command()
    @commands.check(lambda ctx: ctx.author.guild_permissions.manage_roles)
    async def register(
            self,
            ctx: Context,
            arg: str
    ) -> None:
        sync_roles(ctx)

        # Try to get current guild.
        guild = Guild.objects.get(uid=ctx.guild.id)

        # Argument must be an exact name of the role to be made public.
        for role in ctx.guild.roles:
            if role.name == arg:
                PublicRole.objects.get_or_create(
                    uid=role.id,
                    guild=guild,
                )
                await ctx.success()
                return

        await ctx.post(
            Message.danger('There is no `{}` role.'.format(arg))
        )

    @publicroles.command()
    @commands.check(lambda ctx: ctx.author.guild_permissions.manage_roles)
    async def unregister(
            self,
            ctx: Context,
            arg: str
    ) -> None:
        sync_roles(ctx)

        # Argument must be an exact name of the role that's public.
        # Find out the role uid first.
        for role in ctx.guild.roles:
            if role.name == arg:
                try:  # Try to delete the role.
                    PublicRole.objects.get(uid=role.id).delete()
                    await ctx.success()
                    return
                except PublicRole.DoesNotExist:
                    await ctx.post(
                        Message.danger(
                            'Role `{}` is not public.'.format(arg)
                        )
                    )
                    return

        await ctx.post(
            Message.danger('There is no `{}` role.'.format(arg))
        )

    @publicroles.command()
    @commands.check(lambda ctx: ctx.author.guild_permissions.manage_roles)
    async def create(
            self,
            ctx: Context,
            arg: str
    ) -> None:
        sync_roles(ctx)

        # Get current guild.
        guild = Guild.objects.get(uid=ctx.guild.id)

        # There should not be a server role with such name.
        for role in ctx.guild.roles:
            if slugify(role.name) == slugify(arg):
                await ctx.post(Message.danger(
                    'Role `{}` already exists.'.format(arg)
                ))
                return

        # Now it's safe to create a new role.
        try:
            r = await ctx.guild.create_role(
                name=arg,
            )
        except Forbidden as e:
            await ctx.post(Message.danger(str(e)))
            return

        # Save the role locally as public.
        PublicRole(guild=guild, uid=r.id).save()

        await ctx.success()
