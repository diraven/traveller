"""Paginators for different data types."""
import abc
import asyncio
import math
import typing as t

import discord
import pymongo

from core.utils import Button

from core.context import Context

DEFAULT_SEPARATOR = "\n"


class Base:
    """Base paginator functionality."""

    def __init__(self, *, ctx: Context, title: str, timeout: int = 10):
        """Initialize base paginator functionality."""
        self._ctx = ctx
        self._title = title
        self._current = 1
        self._timeout = timeout
        self._count = 0
        self._posted_msg: discord.Message = None

    @abc.abstractmethod
    async def load(self, data) -> None:
        """Load data into the paginator."""

    @property
    @abc.abstractmethod
    async def _embed(self) -> discord.Embed:
        """Get current page as embed."""

    async def _update(self) -> None:
        try:
            await self._posted_msg.edit(embed=await self._embed)
        except AttributeError:
            self._posted_msg = await self._ctx.send(
                embed=await self._embed,
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
            return all(
                (
                    reaction.emoji
                    in (
                        Button.ARROW_LEFT.value,
                        Button.ARROW_RIGHT.value,
                    ),
                    reaction.message.id == self._posted_msg.id,
                    user.id == self._ctx.message.author.id,
                )
            )

        done, pending = await asyncio.wait_for(
            asyncio.wait(
                [
                    asyncio.create_task(
                        self._ctx.bot.wait_for(
                            "reaction_add",
                            check=check,
                        )
                    ),
                    asyncio.create_task(
                        self._ctx.bot.wait_for(
                            "reaction_remove",
                            check=check,
                        )
                    ),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            ),
            timeout=self._timeout,
        )
        for task in pending:
            task.cancel()

        for task in done:
            embed = await self._embed
            embed.description += " **Loading...**"
            await self._posted_msg.edit(embed=embed)

            reaction, _ = task.result()

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
        title: str,
        separator: str = DEFAULT_SEPARATOR,
        timeout: int = 10,
    ):
        """Initialize list paginator."""
        super().__init__(ctx=ctx, title=title, timeout=timeout)
        self._separator = separator

        self._pages: t.List[str] = []

    async def load(self, data: t.List) -> None:
        """Load list into the paginator."""
        length = 0
        start = 0
        items = [str(item) for item in data]
        for i, item in enumerate(items):
            delta = len(self._separator) + len(item)
            if length + delta > self._max_page_len:
                self._pages.append(self._separator.join(items[start:i]))
                start = i
                length = 0
            length += delta
        self._pages.append(
            self._separator.join(items[start:]) or "None",
        )
        self._count = len(self._pages)

    @property
    async def _embed(self) -> discord.Embed:
        """Get current page as embed."""
        return discord.Embed(
            title=self._title,
            color=discord.Color.blue(),
            description=f"{self._pages[self._current - 1]}\n"
            f"Page: {self._current}/{self._count}",
        )


async def post_from_list(
    *,
    ctx: Context,
    data: t.List,
    title: str,
    separator: str = DEFAULT_SEPARATOR,
    timeout: int = 10,
):
    """Post paginator from list."""
    paginator = List(
        ctx=ctx,
        title=title,
        separator=separator,
        timeout=timeout,
    )
    await paginator.load(data)
    await paginator.post()


class Motor(Base):
    """Paginates motor queryset."""

    _per_page = 10

    def __init__(
        self,
        *,
        ctx: Context,
        title: str,
        formatter: t.Callable = str,
        separator: str = DEFAULT_SEPARATOR,
        timeout: int = 10,
    ):
        """Initialize list paginator."""
        super().__init__(ctx=ctx, title=title, timeout=timeout)
        self._separator = separator
        self._collection = None
        self._filter = None
        self._formatter = formatter

    async def load(self, data: pymongo.cursor.Cursor) -> None:
        """Load data from pymongo cursor."""
        self._collection = data.collection
        self._filter = data.delegate._Cursor__spec  # pylint: disable=protected-access
        docs_count = await self._collection.count_documents(  # type: ignore
            self._filter,
        )
        self._count = math.ceil(float(docs_count) / float(self._per_page))

    @property
    async def _embed(self) -> discord.Embed:
        """Get current page as embed."""
        skip = (self._current - 1) * self._per_page
        records = (
            await self._collection.find(  # type: ignore
                self._filter,
            )
            .skip(skip)
            .limit(self._per_page)
            .to_list(self._per_page)
        )

        formatted_records = map(self._formatter, records)
        return discord.Embed(
            title=self._title,
            color=discord.Color.blue(),
            description=f"{self._separator.join(formatted_records)}\n"
            f"Page: {self._current}/{self._count}",
        )


async def post_from_motor(
    *,
    ctx: Context,
    data: pymongo.cursor.Cursor,
    title: str,
    formatter: t.Callable = str,
    separator: str = DEFAULT_SEPARATOR,
    timeout: int = 10,
):
    """Post paginator from motor cursor."""
    paginator = Motor(
        ctx=ctx,
        title=title,
        separator=separator,
        timeout=timeout,
        formatter=formatter,
    )
    await paginator.load(data)
    await paginator.post()
