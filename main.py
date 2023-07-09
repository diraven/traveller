from discord.ext import commands

import settings
from cogs import faq, rusni_pyzda, slap, sum20, sum_

bot = commands.Bot("!", intents=settings.intents)


@bot.event
async def on_ready() -> None:
    for module in [
        faq,
        rusni_pyzda,
        slap,
        sum20,
        sum_,
    ]:
        await module.setup(bot)

    for guild in bot.guilds:
        synced = await bot.tree.sync(guild=guild)
        print(f"{guild.name}: {len(synced)} cmds synced")


bot.run(settings.DISCORD_BOT_TOKEN)
