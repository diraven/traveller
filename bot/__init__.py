from typing import Any

from discord.ext import commands

from bot.db import DB


class Bot(commands.Bot):
    async def close(self) -> None:
        await DB.disconnect()
        await super().close()

    async def on_command_error(self, context, exception) -> Any:
        # TODO
        return await super().on_command_error(context, exception)
