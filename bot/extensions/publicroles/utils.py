import asyncio
import re
from typing import Optional, List

import editdistance
from discord import Role
from django.utils.text import slugify as django_slugify

from core import Context
from extensions.publicroles.models import PublicRole


def slugify(text: str) -> str:
    text = re.sub(r'\s', '', text).strip().lower()
    return django_slugify(text)


def sync(ctx: Context) -> None:
    """
    Synchronizes locally stored list of roles with the real server roles.
    """
    # Get all stored public roles.
    stored_public_roles = await PublicRole.get_all(ctx.guild.id)

    # Get a list of real roles of the server.
    real_roles = {}
    for discord_role in ctx.guild.roles:
        real_roles[discord_role.id] = discord_role

    # Delete all roles we have stored locally that do not exist on the server
    # any more.
    for stored_role in stored_public_roles:
        if stored_role.discord_id not in real_roles.keys():
            stored_role.delete()


def format_list(items: List[Role], offset: int = 0) -> Tuple[str, int]:
    """
    Converts discord roles list to the string representation. Limited to 1000
    symbols.
    """
    if items:
        names = []
        length = 0
        # For eash item after an offset.
        for item in items[offset:]:
            # Calculate resulting string length.
            length += len(str(item))
            # If list is too large - stop adding further.
            if length > 1000:
                break
            # Add item to the list.
            names.append(item.name)
            # Adjust offset.
            offset += 1
        # Prepare result.
        result = ", ".join(['`{}`'.format(name) for name in names])
        # Offset already contains count of names, so we should not add it here.
        if offset < len(items):
            # Post a message notifying of leftover items.
            result += "... Click button below to see {} more.".format(
                len(items) - offset
            )
        return result, offset
    else:
        return "Nothing found.", offset


async def post_list(
        ctx: Context,
        items: List,
        offset: int = 0,
        title: str = None
):
    result, offset = format_list(items, offset)
    message = await ctx.post(Message(result, title))
!!!!!!!!!!
    if offset < len(items):
        # Emoji to be used as button.
        emoji = '▶'

        # Add emoji.
        await ctx.react(emoji, message)

        def check(reaction: Reaction, user: User):
            return user == ctx.author and str(reaction.emoji) == emoji

        try:
            await ctx.bot.wait_for(
                'reaction_add',
                timeout=20.0,
                check=check,
            )
            await post_list(ctx, items, offset, title)
        except asyncio.TimeoutError:
            await message.remove_reaction(emoji, ctx.me)


async def search(
        ctx: Context, roles: List[Role], arg: str
) -> Optional[List[Role]]:
    """
    Performs fuzzy search for the given arg among all server public roles. Returns multiple roles.
    """

    # Get all public roles for the guild.
    public_roles_ids = PublicRole.get_all(guild_discord_id=ctx.guild.id)

    # Now search guild roles list for the term provided.
    result = []

    # Strict search.
    for role in roles:
        if role.id in public_roles_ids and arg == role.name:
            result.append(role)
    if result:
        return result

    # Partial match search.
    for role in roles:
        if role.id in public_roles_ids and slugify(arg) in slugify(role.name):
            result.append(role)
    if result:
        return result

    # Fuzzy search.
    for role in roles:
        if role.id in public_roles_ids and \
                editdistance.eval(
                    slugify(role.name),
                    slugify(arg),
                ) < 2:
            result.append(role)
    return result

# async def search_one(
#         ctx: Context,
#         roles: List[Role],
#         arg: str
# ) -> Optional[Role]:
#     """
#     Performs fuzzy search for the given arg among all server public roles. Returns one role if found, empty list
#     """
#
#     result = await fuzzy_search_public_roles(ctx, roles, arg)
#
#     # Set symbols limit to optimize search results.
#     if 0 < len(arg) < 3:
#         await ctx.post(
#             Message.danger('Search must contain at least 3 symbols.')
#         )
#         return None
#
#     # If no roles found.
#     if len(result) == 0:
#         await ctx.post(Message.danger('Role not found.'))
#
#     # If one role found.
#     if len(result) == 1:
#         return result[0]
#
#     # If multiple roles found.
#     if len(result) > 1:
#         await post_list(ctx, result, title='Multiple roles found')
#
#     return None
