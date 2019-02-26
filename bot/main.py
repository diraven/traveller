from core.bot import Bot
from settings import settings

# Create bot instance.
instance = Bot()

# Load bot extensions.
instance.load_extension('extensions.test')

# Run the bot.
instance.run(settings.DISCORD_TOKEN, bot=True, reconnect=True)
