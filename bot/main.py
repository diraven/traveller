from bot import Bot, settings_local
from bot.get_prefix import get_prefix
from bot.init_db import init_db

# Create bot instance.
instance = Bot(
    command_prefix=get_prefix,
    description='A Rewrite Cog Example',
)

# Schedule db init function for execution.
instance.loop.create_task(init_db())

# Load all the bot's extensions.
instance.load_extension('extensions.base')

# Run the bot.
instance.run(settings_local.DISCORD_TOKEN, bot=True, reconnect=True)
