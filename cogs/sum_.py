import aiohttp
import discord
from bs4 import BeautifulSoup, Tag
from discord.ext import commands

import models


class SumCog(models.Cog):
    @discord.app_commands.command(  # type: ignore
        description="Словник української мови (sum.in.ua)",
    )
    @discord.app_commands.guild_only()
    async def sum(
        self, interaction: discord.Interaction[commands.Bot], word: str
    ) -> None:
        async with aiohttp.ClientSession() as session:
            url = f"http://sum.in.ua/?swrd={word}"
            embed = discord.Embed()
            embed.set_author(name="sum.in.ua", url=url)

            async with session.get(url) as resp:
                data = await resp.text()
                soup = BeautifulSoup(data, "html.parser")
                articles = soup.select(
                    "div[itemtype='http://schema.org/ScholarlyArticle']"
                )

                # No articles found.
                if len(articles) == 0:
                    embed.description = f"Слово не знайдено. Що в біса таке '{word}'?"

                # At least one article found.
                if len(articles) > 0:
                    article: Tag = articles[0]
                    tag_body = article.select_one("div[itemprop='articleBody']")
                    text = tag_body.text if tag_body else "Текст не знайдено"
                    embed.description = (
                        text if len(text) < 2000 else f"{text[:2000]}..."
                    )
                    tag_tom = article.select_one("p.tom")
                    footer = tag_tom.text if tag_tom else "Том не знайдено"
                    embed.set_footer(
                        text=footer if len(footer) < 1000 else f"{footer[:1000]}..."
                    )

                    if len(articles) > 1:
                        embed.description += (
                            f"\n\nСлово має [більше одного значення]({url})."
                        )

            await interaction.response.send_message(
                embed=embed,
            )
