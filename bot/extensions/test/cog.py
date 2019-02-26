from discord import Color
from discord.ext import commands

from core import CogBase, Context, EMOJI_UNICODE, Message


class Cog(CogBase):
    @commands.group(invoke_without_command=True)
    async def test(self, ctx: Context):
        await ctx.message.add_reaction(EMOJI_UNICODE[':crab:'])

    @test.command()
    async def message(self, ctx: Context) -> None:
        """Tests message-type response."""
        await ctx.post(
            Message(
                text="text",
                # title="title",
                icon=EMOJI_UNICODE[':crab:'],
                color=Color.dark_green()),
        )

    @test.command()
    async def mention(self, ctx: Context) -> None:
        """Tests mention-type response."""
        await ctx.post(
            Message(
                text="text",
                icon=EMOJI_UNICODE[':crab:'],
                color=Color.dark_green(),
            ),
            with_mention=True,
        )

    @test.command()
    async def reaction(self, ctx: Context) -> None:
        """Tests reactions."""
        await ctx.message.add_reaction(EMOJI_UNICODE[':question_mark:'])
        await ctx.message.clear_reactions()
        await ctx.message.add_reaction(EMOJI_UNICODE[':OK_button:'])
