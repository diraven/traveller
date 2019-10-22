"""Main bot module."""
import logging

from core.bot import Bot
from settings import settings
from settings.settings import DEBUG

instance = Bot()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)


# Register on ready event.
@instance.event
async def on_ready() -> None:
    """Notify that bot is ready."""
    logger.info('Bot is now running.')


# Load bot extensions.
instance.load_extension('extensions.owner')
instance.load_extension('extensions.publicroles')
instance.load_extension('extensions.mod')
instance.load_extension('extensions.autorole')

# Run the bot.
instance.run(settings.DISCORD_TOKEN, bot=True, reconnect=True)
