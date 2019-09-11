"""Publicroles cog module."""

from discord.ext import commands

from core.cogbase import CogBase
from core.context import Context
from core.message import Message
from core.models import Guild


class Cog(CogBase):
    """Core cog."""

    @commands.group(
        invoke_without_command=True,
    )
    async def alias(
            self,
            ctx: Context,
            *args: str,
    ) -> None:
        """Show available aliases."""
        guild, _ = await Guild.get_or_create(ctx.guild.id)
        print(guild.get('aliases', []))

        # TODO: Format and output as paginator.
        # guild = guilds.g
        #
        # guilds = ctx.bot.db.guilds
        # print('result %s' % repr(result.inserted_id))
        #
        # await utils.Paginator(
        #     ctx=ctx,
        #     member=ctx.author,
        #     items=['jhg'],
        #     separator='\n',
        #     timeout=60,
        #     title='public roles found',
        #     color=discord.Color.blue(),
        # ).post()

    @alias.command()
    async def add(
            self,
            ctx: Context,
            *args: str,
    ) -> None:
        """Output your public roles."""
        # TODO: Verify permissions.
        if len(args) != 2:
            await ctx.post(Message.danger(
                'Exactly 2 parameters must be provided for this command.',
            ))
            return
        result = await Guild.add_alias(
            guild_id=ctx.guild.id,
            src=args[0],
            dst=args[1],
        )
        if result.modified_count:
            await ctx.ok()
        else:
            await ctx.post(Message.danger(
                'Such alias already exists.',
            ))

    # TODO: alias del command
