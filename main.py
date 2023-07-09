from discord.ext import commands

import settings
from cogs import faq, rusni_pyzda, slap, sum20

bot = commands.Bot("!", intents=settings.intents)


@bot.event
async def on_ready() -> None:
    await faq.setup(bot)
    await rusni_pyzda.setup(bot)
    await slap.setup(bot)
    await sum20.setup(bot)

    for guild in bot.guilds:
        synced = await bot.tree.sync(guild=guild)
        print(f"{guild.name}: {len(synced)} cmds synced")


bot.run(settings.DISCORD_BOT_TOKEN)
