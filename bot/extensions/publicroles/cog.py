"""Publicroles cog module."""

import typing
import discord
from discord.ext import commands
import Levenshtein

import core
from core import utils

MAX_EDIT_DISTANCE = 3


async def find_public_role(
        ctx: core.Context,
        term: str,
        provided_roles: typing.Optional[typing.List[discord.Role]] = None,
        title: typing.Optional[str] = 'roles found'
) -> typing.Optional[discord.Role]:
    """Find exactly one public role or output message if multiple found."""
    roles = await find_public_roles(ctx, term, provided_roles)
    if len(roles) == 1:
        return roles[0]
    else:
        await utils.Paginator(
            ctx=ctx,
            member=ctx.author,
            items=[role.mention for role in roles],
            separator=', ',
            timeout=60,
            title=title,
            color=discord.Color.blue(),
        ).post()


async def find_public_roles(
        ctx: core.Context,
        term: typing.Optional[str] = None,
        provided_roles: typing.Optional[typing.List[discord.Role]] = None,
) -> typing.List[discord.Role]:
    """Filter public roles with term provided."""
    all_public_roles = []
    for role in ctx.guild.roles[1:]:
        if role.name == 'public-roles':
            break
        all_public_roles.append(role)
    all_public_roles_ids = [role.id for role in all_public_roles]

    if provided_roles:
        roles = [
            role for role in provided_roles
            if role.id in all_public_roles_ids
        ]
    else:
        roles = all_public_roles

    roles = sorted(roles, key=lambda x: len(x.members), reverse=True)

    if not term:
        return roles

    term = term.lower()
    filtered_roles = []
    for role in roles:
        if term == role.name.lower():
            filtered_roles.append(role)

    if not filtered_roles:
        for role in roles:
            if role.name.lower().startswith(term):
                filtered_roles.append(role)
        if filtered_roles:
            return filtered_roles

    if not filtered_roles:
        for role in roles:
            if term in role.name.lower():
                filtered_roles.append(role)
        if filtered_roles:
            return filtered_roles

    if not filtered_roles:
        for role in roles:
            if Levenshtein.distance(
                    term,
                    role.name.lower(),
            ) <= MAX_EDIT_DISTANCE:
                filtered_roles.append(role)

    return filtered_roles


class Cog(core.CogBase):
    """Publicroles cog."""

    @commands.group(
        invoke_without_command=True,
    )
    async def publicroles(
            self,
            ctx: core.Context,
            arg: typing.Optional[str] = None,
    ) -> None:
        """Show available public roles."""
        if 'public-roles' not in [role.name for role in ctx.guild.roles]:
            await ctx.post(core.Message.danger(
                text='I\'m unable to find `public-roles` role.\n'
                     'Please make a role named `public-roles` and make sure '
                     'it\'s above all of the public roles like this:\n'
                f'- `{ctx.bot.user.display_name}`\n'
                     '- `some-other-role1`\n'
                     '- `some-other-role2`\n'
                     '- ...\n'
                     '- `public-roles`\n'
                     '- `public-role-1`\n'
                     '- `public-role-2`\n'
                     '- `public-role-3`\n'
                     '- ...\n'
                     '- `@everyone`\n'
            ))
            return

        roles = await find_public_roles(ctx, arg)
        await utils.Paginator(
            ctx=ctx,
            member=ctx.author,
            items=[role.mention for role in roles],
            separator=', ',
            timeout=60,
            title=f'available public roles',
            color=discord.Color.blue(),
        ).post()

    @publicroles.command()
    async def my(
            self,
            ctx: core.Context,
            arg: typing.Optional[str] = None,
    ) -> None:
        """Output your public roles."""
        roles = await find_public_roles(ctx, arg, ctx.author.roles)
        await utils.Paginator(
            ctx=ctx,
            member=ctx.author,
            items=[role.mention for role in roles],
            separator=', ',
            timeout=60,
            title=f'public roles for @{ctx.author.display_name}',
            color=discord.Color.blue(),
        ).post()

    @publicroles.command()
    async def who(
            self,
            ctx: core.Context,
            arg: str,
    ) -> None:
        """Show who has this public role."""
        role = await find_public_role(ctx, arg)
        if role:
            members = sorted([
                member for member in ctx.guild.members if role in member.roles
            ], key=lambda x: x.display_name)

            await utils.Paginator(
                ctx=ctx,
                member=ctx.author,
                items=[member.mention for member in members],
                separator=', ',
                timeout=60,
                no_data_str='no one',
                title=f'members with "{role.name}" role',
                color=discord.Color.blue(),
            ).post()

    @publicroles.command()
    async def join(
            self,
            ctx: core.Context,
            arg: str,
    ) -> None:
        """Get yourself a public role."""
        role = await find_public_role(ctx, arg)
        if role:
            await ctx.author.add_roles(role)
            await ctx.ok()

    @publicroles.command()
    async def leave(
            self,
            ctx: core.Context,
            arg: str,
    ) -> None:
        """Remove public role from yourself."""
        role = await find_public_role(ctx, arg, ctx.author.roles)
        if role:
            await ctx.author.remove_roles(role)
            await ctx.ok()

    @publicroles.command()
    async def stats(
            self,
            ctx: core.Context,
    ) -> None:
        """Show public roles stats."""
        roles = await find_public_roles(ctx)

        await utils.Paginator(
            ctx=ctx,
            member=ctx.author,
            items=[f'{role.mention} ({len(role.members)})' for role in roles],
            separator='\n',
            timeout=60,
            no_data_str='no one',
            title=f'public roles stats',
            color=discord.Color.blue(),
        ).post()

# Expected commands: stats
