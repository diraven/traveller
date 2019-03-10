"""Bot generic utilities module."""
import asyncio
import enum
import math
import typing

import discord

import core
from core import Context, EMOJI_ALIAS_UNICODE

PER_PAGE = 5
TIMEOUT = 10


@enum.unique
class Button(enum.Enum):
    """Chooser control button."""

    ARROW_LEFT = EMOJI_ALIAS_UNICODE[':arrow_backward:']
    ARROW_RIGHT = EMOJI_ALIAS_UNICODE[':arrow_forward:']
    OPTION_1 = '\U0001F1E6'
    OPTION_2 = '\U0001F1E7'
    OPTION_3 = '\U0001F1E8'
    OPTION_4 = '\U0001F1E9'
    OPTION_5 = '\U0001F1EA'

    @classmethod
    def values(cls) -> typing.List[str]:
        """Button values."""
        return [b.value for b in cls]

    @classmethod
    def options(cls) -> typing.Iterable['Button']:
        """Buttons for options selection."""
        return (getattr(cls, f'OPTION_{i + 1}') for i in range(PER_PAGE))


class Chooser:
    """
    Present user with choice.

    Call the callback for every choice user has made. Allows navigation
    over items list.
    """

    def __init__(
            self, *,
            ctx: Context,
            user: discord.User,
            items: typing.Collection,
            callback: typing.Callable,
            timeout: int = TIMEOUT,  # seconds
            multiple: bool = False,
            title: str = None,
            icon: str = None,
            color: discord.Color = None,
    ) -> None:
        """Make new chooser."""
        self.ctx = ctx
        self.user = user
        self.items = items
        self.callback = callback
        self.multiple = multiple
        self.timeout = timeout
        self.posted_msg: discord.Message = None

        self.message = core.Message(
            title=title,
            icon=icon,
            color=color,
            text='',
        )

        self.page = 1

    @property
    def pages(self) -> int:
        """Calculate total amount of pages."""
        return math.ceil(len(self.items) / PER_PAGE)

    async def _update(self) -> None:
        start = (self.page - 1) * PER_PAGE
        end = min(self.page * PER_PAGE, len(self.items))
        items = self.items[start:end]
        choices = dict(zip(
            (b.value for b in Button.options()),
            items,
        ))
        self.message.text = '\n'.join(
            f'{emoji} {choice}' for emoji, choice in choices.items()
        )

        self.message.text += f'\nPage: {self.page}/{self.pages}'

        if self.posted_msg:
            await self.posted_msg.edit(
                embed=self.message.as_embed(),
            )
        else:
            self.posted_msg = await self.ctx.send(
                embed=self.message.as_embed(),
            )
            await self.posted_msg.add_reaction(Button.ARROW_LEFT.value)
            await self.posted_msg.add_reaction(Button.ARROW_RIGHT.value)
            for b in Button.options():
                await self.posted_msg.add_reaction(b.value)

        def check(
                reaction: discord.Reaction,
                user: discord.User,
        ) -> bool:
            return all((
                reaction.emoji in tuple(choices.keys()) + (
                    Button.ARROW_LEFT.value,
                    Button.ARROW_RIGHT.value,
                ),
                reaction.message.id == self.posted_msg.id,
                user.id == self.user.id,
            ))

        done, pending = await asyncio.wait_for(
            asyncio.wait(
                [
                    asyncio.create_task(self.ctx.bot.wait_for(
                        'reaction_add',
                        check=check,
                    )),
                    asyncio.create_task(self.ctx.bot.wait_for(
                        'reaction_remove',
                        check=check,
                    )),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            ),
            timeout=self.timeout,
        )
        for task in pending:
            task.cancel()

        for task in done:
            self.message.text += ' **Loading...**'
            await self.posted_msg.edit(
                embed=self.message.as_embed(),
            )

            reaction, user = task.result()

            if reaction.emoji == Button.ARROW_LEFT.value:
                if self.page > 1:
                    self.page -= 1
                return

            if reaction.emoji == Button.ARROW_RIGHT.value:
                if self.page < self.pages:
                    self.page += 1
                return

            if self.callback:
                await self.callback(choices[reaction.emoji], user)
                return

    async def post(self):
        """Post a chooser message."""
        try:
            # Get a timeout exception from the other event handler that
            while True:
                await self._update()
                if not self.multiple:
                    break
        except asyncio.TimeoutError:
            await self.posted_msg.clear_reactions()
