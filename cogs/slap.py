import random

import discord
from discord.ext import commands

import settings

# pylint: disable=line-too-long
TEMPLATES = (
    "{} прикладає {} по спині величезним сомом.",
    "{} демонструє {} щорічну заяву Арестовича на звільнення.",
    "{} щось кричить {} на вухо.",
    "{} уважно дивиться {} в очі.",
    "{} хизується електрохарчуванням перед {}.",
    '{} шепоче {} на вухо "русні пизда".',
    "{} шепоче {} на вухо що стало краще.",
    "{} шепоче {} на вухо що стало гірше.",
    '{} показує {} пальцем на напис "зрада".',
    '{} показує {} пальцем на напис "перемога".',
    '{} показує {} пальцем на напис "переможна зрада".',
    '{} показує {} пальцем на напис "зраджена перемога".',
    '{} показує {} пальцем на напис "зрадоперемога".',
    "{} підозріло зиркає на {}.",
    "{} тихенько ліпить слоупока {} на спину.",
    "{} бідкається, {} розводить руками.",
    '{} каже {} "Це ж було вже!".',
    "{} вмовляє {} проголосувати за Ляшка.",
    "{} демонструє свої музичні здібності. {} плаче.",
    "{} демонструє свої вокальні здібності. {} плаче.",
    '{} демонструє супер сайян. {} каже "ок".',
    "{} конем б'є короля у {}. Це гол.",
    "{} п'є чай з молоком. {} каже що це мєрзость.",
    "{} робить {} комплімент. Це надзвичайно ефективно!",
    "{} обіймає {}. Всі інші заздрять.",
    "{} нагадує {} що пора на завод.",
    "{} пропонує {} виміряти довжину мосту.",
    "{} пропонує {} розкрутитися.",
    "{} slaps {} around with small 50Lbs Linux manual.",
    "{} пропонує {} зупинитися і послухати.",
    "{} просить {} покликати його мішок з м'ясом.",
)


class SlapCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot
        super().__init__()

    @discord.app_commands.command(description="Йой!")  # type: ignore
    @discord.app_commands.guilds(discord.Object(id=settings.GUILD_ID))
    @discord.app_commands.guild_only()
    async def slap(
        self, interaction: discord.Interaction[commands.Bot], member: discord.Member
    ) -> None:
        embed = discord.Embed(
            title="Йой!",
            description=random.choice(TEMPLATES).format(  # nosec
                interaction.user.mention, member.mention
            ),
            color=discord.Color.blue(),
        )

        await interaction.response.send_message(
            embed=embed,
        )
