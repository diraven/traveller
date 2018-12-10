from bot.core import Bot, get_prefix, init_db
from bot.settings import settings

# Create bot instance.
instance = Bot(
    command_prefix=get_prefix,
    description='A Rewrite Cog Example',
)

# Schedule db init function for execution.
instance.loop.create_task(init_db())

# Load all the bot's extensions.
instance.load_extension('extensions.test')

# Run the bot.
instance.run(settings.DISCORD_TOKEN, bot=True, reconnect=True)
