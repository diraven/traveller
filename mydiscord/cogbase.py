from mydiscord.bot import MyBot


class CogBase:
    _bot = None  # type: MyBot

    def __init__(self, bot: MyBot) -> None:
        self._bot = bot
