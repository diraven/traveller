import discord
from discord.ext import commands

import settings
from cogs import faq, rusni_pyzda

bot = commands.Bot("!", intents=settings.intents)


@bot.event
async def on_ready() -> None:
    await bot.add_cog(faq.FaqCog(bot))
    await bot.add_cog(rusni_pyzda.RusniPyzdaCog(bot))

    synced = await bot.tree.sync(guild=discord.Object(id=settings.GUILD_ID))
    print(f"{len(synced)} cmds synced!")


bot.run(settings.DISCORD_BOT_TOKEN)
