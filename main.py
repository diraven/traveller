import discord
import sqlalchemy.orm as sa_orm
from discord.ext import commands

import models
import settings
from cogs import configuration, faq, rusni_pyzda, slap, sum20, sum_

if settings.SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        max_breadcrumbs=50,
        debug=settings.DEBUG,
        traces_sample_rate=1.0,
        release="0.0.1",
    )

bot = commands.Bot("!", intents=settings.intents)


@bot.tree.error
async def error_handler(
    interaction: discord.Interaction[commands.Bot],
    error: Exception,
) -> None:
    embed = discord.Embed(
        color=discord.Color.red(),
        title="Помилка",
    )
    if isinstance(error, discord.app_commands.MissingPermissions):
        embed.description = "Відсутній доступ."
    else:
        raise error
    await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
    )


@bot.event
async def on_ready() -> None:
    for module in [
        configuration,
        faq,
        rusni_pyzda,
        slap,
        sum_,
        sum20,
    ]:
        await module.setup(bot)

    with sa_orm.Session(models.engine) as session:
        for guild in bot.guilds:
            session.merge(models.Guild(id=guild.id, name=guild.name))
            # Sync commands.
            synced = await bot.tree.sync(guild=guild)
            print(f"{guild.name}: {len(synced)} cmds synced")

        # Save guilds we are connected to.
        session.commit()


bot.run(settings.DISCORD_BOT_TOKEN)
