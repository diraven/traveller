from typing import List

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
    public_roles_uids = PublicRole.objects.filter(
        guild__uid=ctx.guild.id,
    ).values_list('uid', flat=True)

    # Get a list of real roles of the server.
    real_roles = {}
    for discord_role in ctx.guild.roles:
        real_roles[discord_role.id] = discord_role

    # Delete all roles we have stored locally that do not exist on the server
    # any more.
    for uid in public_roles_uids:
        if uid not in real_roles.keys():
            PublicRole.objects.get(uid=uid).delete()


def format_list(items: List[Role]) -> str:
    """
    Converts discord roles list to the string representation. Limited to 1000
    symbols.
    """
    if items:
        names = []
        length = 0
        for item in items:
            length += len(str(item))
            if length > 1000:
                break
            names.append(item.name)
        result = ", ".join(['`{}`'.format(name) for name in names])
        if len(names) < len(items):
            result += " and {} more...".format(len(items) - len(names))
        return result
    else:
        return "Nothing found."


class Cog(CogBase):
    @commands.group(invoke_without_command=True)
    async def publicroles(
            self,
            ctx: Context,
            arg: str = ""
    ) -> None:
        """
        Searches available public roles.
        """
        sync_roles(ctx)

        # Get a list of stored public roles uids.
        public_roles_uids = PublicRole.objects.filter(
            guild__uid=ctx.guild.id,
        ).values_list('uid', flat=True)

        # Now search guild roles list for the term provided.
        roles = []
        for role in ctx.guild.roles:
            if role.id in public_roles_uids and slugify(arg) in slugify(
                    role.name):
                roles.append(role)

        await ctx.post(Message(format_list(roles), title="Public Roles"))

    @publicroles.command()
    async def my(
            self,
            ctx: Context
    ) -> None:
        """
        Shows public roles you have.
        """
        sync_roles(ctx)

        # Get a list of stored public roles uids.
        public_roles_uids = PublicRole.objects.filter(
            guild__uid=ctx.guild.id,
        ).values_list('uid', flat=True)

        roles = []
        for role in ctx.author.roles:
            if role.id in public_roles_uids:
                roles.append(role)

        await ctx.post(Message(format_list(roles), title="Your Public Roles"))

    @publicroles.command()
    async def join(
            self,
            ctx: Context,
            arg: str = "",
    ) -> None:
        """
        Gives you a public role.
        """
        sync_roles(ctx)

        # Get a list of stored public roles uids.
        public_roles_uids = PublicRole.objects.filter(
            guild__uid=ctx.guild.id,
        ).values_list('uid', flat=True)

        # Find the role of question in the list of server roles and make
        # sure it's public.
        for role in ctx.guild.roles:
            if slugify(role.name) == slugify(
                    arg) and role.id in public_roles_uids:
                try:  # Try to grant the role to the user.
                    await ctx.author.add_roles(role)
                except Forbidden as e:
                    await ctx.post(Message.danger(str(e)))
                    return

                await ctx.success()
                return

        await ctx.post(
            Message.danger('There is no `{}` role.'.format(arg))
        )

    @publicroles.command()
    async def leave(
            self,
            ctx: Context,
            arg: str = "",
    ) -> None:
        """
        Removes you from a public role.
        """
        sync_roles(ctx)

        # Get a list of stored public roles uids.
        public_roles_uids = PublicRole.objects.filter(
            guild__uid=ctx.guild.id,
        ).values_list('uid', flat=True)

        # Find the role of question in the list of server roles and make
        # sure it's public.
        for role in ctx.author.roles:
            if slugify(role.name) == slugify(
                    arg) and role.id in public_roles_uids:
                try:  # Try to grant the role to the user.
                    await ctx.author.remove_roles(role)
                except Forbidden as e:
                    await ctx.post(Message.danger(str(e)))
                    return

                await ctx.success()
                return

        await ctx.post(
            Message.danger('You don\'t have `{}` role.'.format(arg))
        )

    @publicroles.command()
    async def who(
            self,
            ctx: Context,
            arg: str = "",
    ) -> None:
        """
        Shows a list of people who has the public role.
        """
        sync_roles(ctx)

        # Get a role we are interested in.
        for role in ctx.guild.roles:
            if slugify(role.name) == slugify(arg):
                try:  # Try to get the role from our public roles list.
                    PublicRole.objects.get(uid=role.id)
                    members = []
                    for member in ctx.guild.members:
                        for member_role in member.roles:
                            if member_role.id == role.id:
                                members.append(member)

                    await ctx.post(Message(
                        format_list(members),
                        title='People with "{}" public role'.format(arg))
                    )
                    return

                except PublicRole.DoesNotExist:
                    await ctx.post(Message.danger(
                        "The '{}' role is not public.".format(arg)
                    ))
                    return

        await ctx.post(
            Message.danger('There is no `{}` role.'.format(arg))
        )

    @publicroles.command()
    @commands.check(lambda ctx: ctx.author.guild_permissions.manage_roles)
    async def register(
            self,
            ctx: Context,
            arg: str
    ) -> None:
        """
        Registers existing role as a public role.
        """
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
        """
        Unregisters role as a public role.
        """
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
        """
        Creates new role and makes it public.
        """
        sync_roles(ctx)

        # Get current guild.
        guild = Guild.objects.get(uid=ctx.guild.id)

        # There should not be a server role with such name.
        for role in ctx.guild.roles:
            if slugify(role.name) == slugify(arg):
                await ctx.post(Message.danger(
                    'Role `{}` already exists. Try `register` '
                    'instead of `create`.'.format(arg)
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

# stats
