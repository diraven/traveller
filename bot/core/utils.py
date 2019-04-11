"""Bot generic utilities module."""
import asyncio

import enum
import typing
import discord

import core
from core import Context, EMOJI_ALIAS_UNICODE

DEFAULT_TIMEOUT = 10
MAX_PAGE_LEN = 1000


# noinspection PyUnresolvedReferences,PyTypeChecker
@enum.unique
class Button(enum.Enum):
    """Control buttons."""

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

    # @classmethod
    # def options(cls) -> typing.Iterable['Button']:
    #     """Buttons for options selection."""
    #     return (getattr(cls, f'OPTION_{i + 1}') for i in range(PER_PAGE))


class Paginator:
    """Paginates the provided iterable."""

    def __init__(
            self, *,
            ctx: Context,
            member: discord.Member,
            items: typing.List,
            separator: str,
            max_items_per_page: typing.Optional[int] = None,
            no_data_str: str = 'none',
            timeout: int = DEFAULT_TIMEOUT,  # seconds
            title: str = None,
            icon: str = None,
            color: discord.Color = None,
    ) -> None:
        """Make new paginator."""
        self._ctx = ctx
        self._member = member
        self._items = items
        self._separator = separator
        self._max_items_per_page = max_items_per_page
        self._timeout = timeout
        self._no_data_str = no_data_str
        self._posted_msg: discord.Message

        self._message = core.Message(
            title=title,
            icon=icon,
            color=color,
            text='',
        )

        self._current_page_num = 1
        self._pages: typing.List[str] = []
        self._build_pages()

    def _build_pages(self) -> None:
        length = 0
        count = 0
        start = 0
        items = [str(item) for item in self._items]
        for i, item in enumerate(items):
            delta = len(self._separator) + len(item)
            if length + delta > MAX_PAGE_LEN or \
                    count == self._max_items_per_page:
                self._pages.append(self._separator.join(items[start:i]))
                start = i
                length = 0
                count = 0
            length += delta
            count += 1
        self._pages.append(
            self._separator.join(items[start:]) or self._no_data_str
        )

    async def _update(self) -> None:
        self._message.text = self._pages[self._current_page_num - 1]

        if len(self._pages) > 1:
            self._message.text += f'\nPage: {self._current_page_num}/' \
                f'{len(self._pages)}'

        if self._posted_msg:
            await self._posted_msg.edit(
                embed=self._message.as_embed(),
            )
        else:
            self._posted_msg = await self._ctx.send(
                embed=self._message.as_embed(),
            )

        if len(self._pages) == 1:
            raise asyncio.TimeoutError

        await self._posted_msg.add_reaction(Button.ARROW_LEFT.value)
        await self._posted_msg.add_reaction(Button.ARROW_RIGHT.value)

        # noinspection PyShadowingNames
        def check(
                reaction: discord.Reaction,
                user: discord.User,
        ) -> bool:
            return all((
                reaction.emoji in (
                    Button.ARROW_LEFT.value,
                    Button.ARROW_RIGHT.value,
                ),
                reaction.message.id == self._posted_msg.id,
                user.id == self._member.id,
            ))

        done, pending = await asyncio.wait_for(
            asyncio.wait(
                [
                    asyncio.create_task(self._ctx.bot.wait_for(
                        'reaction_add',
                        check=check,
                    )),
                    asyncio.create_task(self._ctx.bot.wait_for(
                        'reaction_remove',
                        check=check,
                    )),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            ),
            timeout=self._timeout,
        )
        for task in pending:
            task.cancel()

        for task in done:
            self._message.text += ' **Loading...**'
            await self._posted_msg.edit(
                embed=self._message.as_embed(),
            )

            reaction, user = task.result()

            if reaction.emoji == Button.ARROW_LEFT.value:
                if self._current_page_num > 1:
                    self._current_page_num -= 1
                return

            if reaction.emoji == Button.ARROW_RIGHT.value:
                if self._current_page_num < len(self._pages):
                    self._current_page_num += 1
                return

    async def post(self) -> None:
        """Post a paginator message."""
        try:
            while True:
                await self._update()
        except asyncio.TimeoutError:
            await self._posted_msg.clear_reactions()
