"""Publicroles cog module."""

import Levenshtein
import discord
import typing
from discord.ext import commands

from core import utils
from core.cogbase import CogBase
from core.context import Context
from core.message import Message
from core.utils import escape

MAX_EDIT_DISTANCE = 2


async def find_public_role(
        ctx: Context,
        term: str,
        provided_roles: typing.Optional[typing.List[discord.Role]] = None,
) -> typing.Optional[discord.Role]:
    """Find exactly one public role or output message if multiple found."""
    roles = await find_public_roles(ctx, term, provided_roles)
    if len(roles) == 1:
        return roles[0]
    elif len(roles) == 0:
        await ctx.post(Message(
            text='none',
            title='roles found',
            color=discord.Color.blue(),
        ))
    else:
        await utils.Paginator(
            ctx=ctx,
            member=ctx.author,
            items=[role.mention for role in roles],
            separator=', ',
            timeout=60,
            title='multiple roles found',
            color=discord.Color.blue(),
        ).post()


async def find_public_roles(
        ctx: Context,
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


class Cog(CogBase):
    """Publicroles cog."""

    @commands.group(
        invoke_without_command=True,
    )
    async def publicroles(
            self,
            ctx: Context,
            *args: str,
    ) -> None:
        """Show available public roles."""
        if 'public-roles' not in [role.name for role in ctx.guild.roles]:
            await ctx.post(Message.danger(
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

        roles = await find_public_roles(ctx, " ".join(args))
        await utils.Paginator(
            ctx=ctx,
            member=ctx.author,
            items=[role.mention for role in roles],
            separator=', ',
            timeout=60,
            title='public roles found',
            color=discord.Color.blue(),
        ).post()

    @publicroles.command()
    async def my(
            self,
            ctx: Context,
            *args: str,
    ) -> None:
        """Output your public roles."""
        roles = await find_public_roles(ctx, " ".join(args), ctx.author.roles)
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
            ctx: Context,
            *args: str,
    ) -> None:
        """Show who has this public role."""
        role = await find_public_role(ctx, " ".join(args))
        if role:
            members = sorted([
                member for member in ctx.guild.members if role in member.roles
            ], key=lambda x: x.display_name)

            await utils.Paginator(
                ctx=ctx,
                member=ctx.author,
                items=[escape(member.display_name) for member in members],
                separator=', ',
                timeout=60,
                no_data_str='no one',
                title=f'members with "{role.name}" public role',
                color=discord.Color.blue(),
            ).post()

    @publicroles.command()
    async def join(
            self,
            ctx: Context,
            *args: str,
    ) -> None:
        """Get yourself a public role."""
        role = await find_public_role(ctx, " ".join(args))
        if role:
            await ctx.author.add_roles(role)
            await ctx.ok()

    @publicroles.command()
    async def leave(
            self,
            ctx: Context,
            *args: str,
    ) -> None:
        """Remove public role from yourself."""
        role = await find_public_role(ctx, " ".join(args), ctx.author.roles)
        if role:
            await ctx.author.remove_roles(role)
            await ctx.ok()

    @publicroles.command()
    async def top(
            self,
            ctx: Context,
    ) -> None:
        """Show public roles stats."""
        roles = await find_public_roles(ctx)

        await utils.Paginator(
            ctx=ctx,
            member=ctx.author,
            items=[f'{role.mention} ({len(role.members)})' for role in roles],
            separator='\n',
            timeout=60,
            max_items_per_page=10,
            no_data_str='no one',
            title='public roles top',
            color=discord.Color.blue(),
        ).post()

# Expected commands: stats
