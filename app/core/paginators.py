"""Paginators for different data types."""
import abc
import asyncio
import typing

import discord

from core.context import Context
from core.utils import Button


class Base:
    """Base paginator functionality."""

    def __init__(self, *, ctx: Context, title: str, timeout: int = 10):
        """Initialize base paginator functionality."""
        self._ctx = ctx
        self._title = title
        self._current = 1
        self._timeout = timeout
        self._count = 0

    @property
    @abc.abstractmethod
    def _embed(self) -> discord.Embed:
        """Get current page as embed."""

    async def _update(self) -> None:
        try:
            await self._posted_msg.edit(embed=self._embed)
        except AttributeError:
            self._posted_msg: discord.Message = await self._ctx.send(
                embed=self._embed,
            )

        if self._count == 1:
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
                user.id == self._ctx.message.author.id,
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
            embed = self._embed
            embed.description += ' **Loading...**'
            await self._posted_msg.edit(embed=embed)

            reaction, user = task.result()

            if reaction.emoji == Button.ARROW_LEFT.value:
                if self._current > 1:
                    self._current -= 1
                return

            if reaction.emoji == Button.ARROW_RIGHT.value:
                if self._current < self._count:
                    self._current += 1
                return

    async def post(self) -> None:
        """Post a paginator message."""
        try:
            while True:
                await self._update()
        except asyncio.TimeoutError:
            await self._posted_msg.clear_reactions()


class List(Base):
    """Paginates list."""

    _max_page_len = 1000

    def __init__(
            self,
            *,
            ctx: Context,
            items: typing.List[str],
            title: str,
            separator: str = '\n',
            timeout: int = 10,
    ):
        """Initialize list paginator."""
        super().__init__(ctx=ctx, title=title, timeout=timeout)

        self._pages: typing.List[str] = []

        length = 0
        start = 0
        items = [str(item) for item in items]
        for i, item in enumerate(items):
            delta = len(separator) + len(item)
            if length + delta > self._max_page_len:
                self._pages.append(separator.join(items[start:i]))
                start = i
                length = 0
            length += delta
        self._pages.append(
            separator.join(items[start:]) or 'None',
        )
        self._count = len(self._pages)

    @property
    def _embed(self) -> discord.Embed:
        """Get current page as embed."""
        return discord.Embed(
            title=self._title,
            color=discord.Color.blue(),
            description=f'{self._pages[self._current - 1]}\n'
                        f'Page: {self._current}/{self._count}',
        )


class Motor(Base):
    """Paginates motor queryset."""
