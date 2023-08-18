from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

API_ROOT_URL = "https://russianwarship.rip/api/v2"


async def setup(bot: commands.Bot) -> None:
    class RusniPyzdaCog(commands.Cog):
        def __init__(self) -> None:
            self._bot = bot
            super().__init__()

        @discord.app_commands.command(  # type: ignore
            description="Втрати РФ станом на сьогодні.",
        )
        @discord.app_commands.guild_only()
        async def rusni_pyzda(
            self, interaction: discord.Interaction[commands.Bot]
        ) -> None:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_ROOT_URL}/statistics/{datetime.today().strftime('%Y-%m-%d')}"
                ) as resp:
                    data = await resp.json()
                    if "errors" in data:
                        embed = discord.Embed(
                            title="Втрати ворога: помилка",
                            description=data["message"],
                            color=discord.Color.red(),
                        )
                    else:
                        data = data["data"]
                        embed = discord.Embed(
                            title="Втрати ворога",
                            url=data["resource"],
                        )
                        for key, val in data["stats"].items():
                            embed.add_field(
                                name=key,
                                value=f"{val} (+{data['increase'][key]})",
                                inline=True,
                            )
                        embed.set_footer(
                            text=f"Станом на {data['date']}, {data['day']}й день війни"
                        )
                        embed.set_thumbnail(
                            url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/"
                            "Emblem_of_the_Ukrainian_Armed_Forces.svg/"
                            "1024px-Emblem_of_the_Ukrainian_Armed_Forces.svg.png"
                        )

                    await interaction.response.send_message(
                        embed=embed,
                    )

    await bot.add_cog(RusniPyzdaCog())
