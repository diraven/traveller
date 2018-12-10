from bot.core import Bot
from bot.core.init_db import init_db
from bot.settings import settings

# Create bot instance.
instance = Bot()

# Schedule db init function for execution.
instance.loop.create_task(init_db())

# Load all the bot's extensions.
instance.load_extension('extensions.test')

# Run the bot.
instance.run(settings.DISCORD_TOKEN, bot=True, reconnect=True)
