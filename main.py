import discord
from discord.ext import commands

import settings
from cogs import faq

bot = commands.Bot("!", intents=settings.intents)


@bot.event
async def on_ready() -> None:
    await bot.add_cog(faq.Cog(bot))

    synced = await bot.tree.sync(guild=discord.Object(id=settings.GUILD_ID))
    print(f"{len(synced)} cmds synced!")


bot.run(settings.DISCORD_BOT_TOKEN)
