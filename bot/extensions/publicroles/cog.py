from discord import Forbidden
from discord.ext import commands

from core import CogBase, Context, Message
from extensions.publicroles.utils import sync, search


class Cog(CogBase):
    @commands.group(invoke_without_command=True)
    async def publicroles(
            self,
            ctx: Context,
            *args
    ) -> None:
        """
        Searches available public roles.
        """
        sync(ctx)  # synchronize locally stored roles with the server

        # Sanitize args.
        arg = ''.join(args)

        # Set symbols limit to optimize search results.
        if 0 < len(arg) < 3:
            await ctx.post(
                Message.danger('Search must contain at least 3 symbols.')
            )
            return None

        roles = await search(ctx, ctx.guild.roles, arg)

        if len(roles) > 0:
            await post_list(ctx, roles, title='Public Roles')
        else:
            await ctx.post(Message.danger("No roles found."))

    @publicroles.command()
    async def my(
            self,
            ctx: Context
    ) -> None:
        """
        Shows public roles you have.
        """
        sync_roles(ctx)

        # Get a list of stored public roles discord_ids.
        public_roles_ids = PublicRole.objects.filter(
            guild__discord_id=ctx.guild.id,
        ).values_list('discord_id', flat=True)

        roles = []
        for role in ctx.author.roles:
            if role.id in public_roles_ids:
                roles.append(role)

        await post_list(ctx, roles, title='Your Public Roles')

    @publicroles.command()
    async def join(
            self,
            ctx: Context,
            *args
    ) -> None:
        """
        Gives you a public role.
        """
        sync_roles(ctx)
        arg = ' '.join(args)

        # Search roles.
        role = await fuzzy_search_public_role(ctx, ctx.guild.roles, arg)

        if role:
            try:
                await ctx.author.add_roles(role)
                await ctx.success()
            except Forbidden as e:
                await ctx.post(Message.danger(str(e)))
            return

    @publicroles.command()
    async def leave(
            self,
            ctx: Context,
            *args
    ) -> None:
        """
        Removes you from a public role.
        """
        sync_roles(ctx)
        arg = ' '.join(args)

        # Search roles.
        role = await fuzzy_search_public_role(ctx, ctx.author.roles, arg)

        if role:
            try:
                await ctx.author.remove_roles(role)
                await ctx.success()
            except Forbidden as e:
                await ctx.post(Message.danger(str(e)))
            return

    @publicroles.command()
    async def who(
            self,
            ctx: Context,
            *args
    ) -> None:
        """
        Shows a list of people who has the public role.
        """
        sync_roles(ctx)
        arg = ' '.join(args)

        # Search roles.
        role = await fuzzy_search_public_role(ctx, ctx.guild.roles, arg)

        if role:
            try:  # Try to get the role from our public roles list.
                PublicRole.objects.get(discord_id=role.id)
                members = []
                for member in ctx.guild.members:
                    for member_role in member.roles:
                        if member_role.id == role.id:
                            members.append(member)

                await post_list(ctx, members,
                                title='People with "{}" public role'.format(
                                    role.name)
                                )
                return

            except PublicRole.DoesNotExist:
                await ctx.post(Message.danger(
                    "The '{}' role is not public.".format(arg)
                ))
                return

    @publicroles.command()
    @commands.check(lambda ctx: ctx.author.guild_permissions.manage_roles)
    async def register(
            self,
            ctx: Context,
            *args
    ) -> None:
        """
        Registers existing role as a public role.
        """
        sync_roles(ctx)
        arg = ' '.join(args)

        # Try to get current guild.
        guild = Guild.objects.get(discord_id=ctx.guild.id)

        # Argument must be an exact name of the role to be made public.
        for role in ctx.guild.roles:
            if role.name == arg:
                PublicRole.objects.get_or_create(
                    discord_id=role.id,
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
            *args
    ) -> None:
        """
        Unregisters role as a public role.
        """
        sync_roles(ctx)
        arg = ' '.join(args)

        # Argument must be an exact name of the role that's public.
        # Find out the role discord_id first.
        for role in ctx.guild.roles:
            if role.name == arg:
                try:  # Try to delete the role.
                    PublicRole.objects.get(discord_id=role.id).delete()
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
            *args
    ) -> None:
        """
        Creates new role and makes it public.
        """
        sync_roles(ctx)
        arg = ' '.join(args)

        # Get current guild.
        guild = Guild.objects.get(discord_id=ctx.guild.id)

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
                mentionable=True,
            )
        except Forbidden as e:
            await ctx.post(Message.danger(str(e)))
            return

        # Save the role locally as public.
        PublicRole(guild=guild, discord_id=r.id).save()

        await ctx.success()
