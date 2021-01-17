"""Publicroles cog module."""

import typing as t

import Levenshtein
import discord
from discord.ext import commands

from core import paginators
from core.cogbase import CogBase
from core.context import Context
from core.utils import escape

MAX_EDIT_DISTANCE = 2
DEFAULT_SEPARATOR = " **|** "
DEFAULT_TIMEOUT = 60


async def find_public_role(
    ctx: Context,
    term: str,
    provided_roles: t.Optional[  # pylint: disable=unsubscriptable-object
        t.List[discord.Role]
    ] = None,
) -> t.Optional[discord.Role]:  # pylint: disable=unsubscriptable-object
    """Find exactly one public role or output message if multiple found."""
    roles = await find_public_roles(ctx, term, provided_roles)
    if len(roles) == 1:
        return roles[0]
    if len(roles) == 0:
        return await ctx.post_info(text="no roles found")
    return await paginators.post_from_list(
        ctx=ctx,
        data=[role.name for role in roles],
        title="multiple roles found",
        separator=DEFAULT_SEPARATOR,
        timeout=DEFAULT_TIMEOUT,
    )


async def find_public_roles(  # pylint: disable=too-many-branches
    ctx: Context,
    term: t.Optional[str] = None,  # pylint: disable=unsubscriptable-object
    provided_roles: t.Optional[  # pylint: disable=unsubscriptable-object
        t.List[discord.Role]
    ] = None,
) -> t.List[discord.Role]:
    """Filter public roles with term provided."""
    all_public_roles = []
    for role in ctx.guild.roles[1:]:
        if role.name == "public-roles":
            break
        all_public_roles.append(role)
    all_public_roles_ids = [role.id for role in all_public_roles]

    if provided_roles:
        roles = [role for role in provided_roles if role.id in all_public_roles_ids]
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
            if (
                Levenshtein.distance(  # pylint: disable=no-member
                    term,
                    role.name.lower(),
                )
                <= MAX_EDIT_DISTANCE
            ):
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
        if "public-roles" not in [role.name for role in ctx.guild.roles]:
            await ctx.post_warning(
                text="'I am unable to find `public-roles` role.\n'"
                "Please make a role named `public-roles` and make sure "
                "it is above all of the public roles like this:\n"
                f"- `{ctx.bot.user.display_name}`\n"
                "- `some-other-role1`\n"
                "- `some-other-role2`\n"
                "- ...\n"
                "- `public-roles`\n"
                "- `public-role-1`\n"
                "- `public-role-2`\n"
                "- `public-role-3`\n"
                "- ...\n"
                "- `@everyone`\n",
            )
            return

        roles = await find_public_roles(ctx, " ".join(args))
        await paginators.post_from_list(
            ctx=ctx,
            data=[role.name for role in roles],
            title="public roles found",
            separator=DEFAULT_SEPARATOR,
            timeout=DEFAULT_TIMEOUT,
        )

    @publicroles.command()
    async def my(  # pylint: disable=invalid-name
        self,
        ctx: Context,
        *args: str,
    ) -> None:
        """Output your public roles."""
        roles = await find_public_roles(ctx, " ".join(args), ctx.author.roles)
        await paginators.post_from_list(
            ctx=ctx,
            data=[role.name for role in roles],
            title=f"public roles for @{ctx.author.display_name}",
            separator=DEFAULT_SEPARATOR,
            timeout=DEFAULT_TIMEOUT,
        )

    @publicroles.command()
    async def who(
        self,
        ctx: Context,
        *args: str,
    ) -> None:
        """Show who has this public role."""
        role = await find_public_role(ctx, " ".join(args))
        if role:
            members = sorted(
                (member for member in ctx.guild.members if role in member.roles),
                key=lambda x: x.display_name,
            )

            await paginators.post_from_list(
                ctx=ctx,
                data=[escape(member.display_name) for member in members],
                title=f'members with "{role.name}" public role',
                separator=DEFAULT_SEPARATOR,
                timeout=DEFAULT_TIMEOUT,
            )

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
            await ctx.react_ok()

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
            await ctx.react_ok()

    @publicroles.command()
    async def top(
        self,
        ctx: Context,
    ) -> None:
        """Show public roles stats."""
        roles = await find_public_roles(ctx)

        await paginators.post_from_list(
            ctx=ctx,
            data=[f"{role.name} ({len(role.members)})" for role in roles],
            title="public roles top",
            separator="\n",
            timeout=DEFAULT_TIMEOUT,
        )


# Expected commands: stats
