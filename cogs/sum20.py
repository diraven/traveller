import aiohttp
import discord
from bs4 import BeautifulSoup
from discord.ext import commands


async def setup(bot: commands.Bot) -> None:
    class Sum20Cog(commands.Cog):
        def __init__(self) -> None:
            self._bot = bot
            super().__init__()

        @discord.app_commands.command(  # type: ignore
            description="Словник української мови (sum20ua.com)",
        )
        @discord.app_commands.guild_only()
        async def sum20(
            self, interaction: discord.Interaction[commands.Bot], word: str
        ) -> None:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://sum20ua.com/api/DictEntry/searchEntry/{word}"
                ) as resp:
                    data = await resp.json()
                    soup = BeautifulSoup(data["entry"], "html.parser")
                    text = soup.text
                embed = discord.Embed(
                    description=text if len(text) < 2000 else f"{text[:2000]}...",
                )
                embed.set_author(name="sum20ua.com", url="https://sum20ua.com")

                await interaction.response.send_message(
                    embed=embed,
                )

    await bot.add_cog(Sum20Cog())
