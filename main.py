import discord
import sqlalchemy.orm as sa_orm
from discord.ext import commands

import models
import settings
from cogs import bans_sharing, configuration, faq, rusni_pyzda, slap, sum20, sum_

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
async def on_guild_join(guild: discord.Guild) -> None:
    # Add new guild to database.
    with sa_orm.Session(models.engine) as session, session.begin():
        session.add(models.Guild(id=guild.id, name=guild.name))
        # Sync commands.
        await bot.tree.sync(guild=guild)


@bot.event
async def on_guild_remove(guild: discord.Guild) -> None:
    with sa_orm.Session(models.engine) as session, session.begin():
        session.query(models.Guild).filter(models.Guild.id == guild.id).delete()


@bot.event
async def on_ready() -> None:
    for module in [
        configuration,
        faq,
        rusni_pyzda,
        slap,
        sum_,
        sum20,
        bans_sharing,
    ]:
        await module.setup(bot)

    with sa_orm.Session(models.engine) as session, session.begin():
        # Add guilds that bot is a member of.
        # We still need this in case if guild was added while bot was offline.
        for guild in bot.guilds:
            session.merge(models.Guild(id=guild.id, name=guild.name))
            # Sync commands.
            await bot.tree.sync(guild=guild)

        # Remove guilds bot is not a member of any more.
        # We still need this in case if guild was removed while bot was offline.
        for stored_guild in session.query(models.Guild):
            if not bot.get_guild(stored_guild.id):
                session.delete(stored_guild)

        # Save guilds we are connected to.
        session.commit()


bot.run(settings.DISCORD_BOT_TOKEN)
