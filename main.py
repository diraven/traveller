import discord
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from discord.ext import commands

import models
import settings
from cogs import bans_sharing, faq, rusni_pyzda, slap, sum20, sum_, verification

if settings.SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        max_breadcrumbs=50,
        debug=settings.DEBUG,
        traces_sample_rate=1.0,
        release="0.0.1",
    )

bot = models.Bot("!", intents=settings.intents)


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
    with models.Session.begin() as session:
        session.add(models.Guild(id_=guild.id, name=guild.name))


@bot.event
async def on_guild_remove(guild: discord.Guild) -> None:
    with models.Session.begin() as session:
        session.delete(models.Guild(id_=guild.id))


@bot.event
async def on_ready() -> None:
    # Add cogs.
    await bot.add_cog(bans_sharing.BansSharingCog(bot=bot))
    await bot.add_cog(faq.FaqCog(bot=bot))
    await bot.add_cog(rusni_pyzda.RusniPyzdaCog(bot=bot))
    await bot.add_cog(slap.SlapCog(bot=bot))
    await bot.add_cog(sum_.SumCog(bot=bot))
    await bot.add_cog(sum20.Sum20Cog(bot=bot))
    await bot.add_cog(verification.VerificationCog(bot=bot))

    # Sync commands.
    if settings.DEBUG and settings.DISCORD_DEV_GUILD_ID:
        guild = bot.get_guild(settings.DISCORD_DEV_GUILD_ID)
        if guild:
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
        else:
            raise RuntimeError(f"guild {settings.DISCORD_DEV_GUILD_ID} not found")
    else:
        await bot.tree.sync()

    with models.Session.begin() as session:
        # Add guilds that bot is a member of.
        # We still need this in case if guild was added while bot was offline.
        for guild in bot.guilds:
            session.merge(models.Guild(id_=guild.id, name=guild.name))

        # Remove guilds bot is not a member of any more.
        # We still need this in case if guild was removed while bot was offline.
        statement = sa.select(models.Guild)
        for stored_guild in session.execute(statement).scalars():
            if not bot.get_guild(stored_guild.id_):
                session.delete(stored_guild)


bot.run(settings.DISCORD_BOT_TOKEN)
