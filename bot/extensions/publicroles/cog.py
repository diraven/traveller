import asyncio
import typing

import discord
from discord.ext import commands

from core import CogBase, Context, EMOJI_ALIAS_UNICODE, Message, utils


class HighlightedRole:
    def __init__(
            self,
            member: discord.Member,
            role: discord.Role
    ):
        self.member: discord.Member = member
        self.role = role
        super().__init__()

    def __str__(self) -> str:
        user_roles_ids = [role.id for role in self.member.roles]
        if self.role.id in user_roles_ids:
            return f'{EMOJI_ALIAS_UNICODE[":white_check_mark:"]}' \
                f'{self.role.mention}'
        return self.role.mention


class Cog(CogBase):
    @commands.group(invoke_without_command=True)
    async def publicroles(
            self,
            ctx: Context,
    ) -> None:
        """
        Shows available public roles.
        """
        roles: typing.List[discord.Role] = ctx.guild.roles
        items = []

        if 'public-roles' not in [role.name for role in roles]:
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

        for role in roles[1:]:
            if role.name == 'public-roles':
                break
            items.append(HighlightedRole(
                ctx.guild.get_member(ctx.author.id),
                role,
            ))

        items = sorted(items, key=lambda item: item.role.name)

        async def callback(
                chosen: HighlightedRole,
                user: discord.User,
        ):
            try:
                member: discord.Member = ctx.guild.get_member(user.id)
                if chosen.role.id in [
                    role.id for role in member.roles
                ]:
                    await member.remove_roles(chosen.role)
                else:
                    await member.add_roles(chosen.role)

                await asyncio.sleep(2)

            except asyncio.TimeoutError:
                await ctx.post(Message.danger(
                    'Failed to update role, something went wrong...'
                ))

        chooser = utils.Chooser(
            ctx=ctx,
            user=ctx.author,
            items=items,
            timeout=60,
            callback=callback,
            multiple=True,
            title=f'Public roles for @{ctx.author.display_name}',
            color=discord.Color.blue(),
        )

        await chooser.post()
