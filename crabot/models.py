import dataclasses
import datetime
import enum
import typing as t

import dateutil.parser


@enum.unique
class ApplicationCommandOptionType(enum.Enum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


@enum.unique
class Color(enum.Enum):
    DEFAULT = 0  # 000000
    AQUA = 1752220  # 1ABC9C
    DARK_AQUA = 1146986  # 11806A
    GREEN = 3066993  # 2ECC71
    DARK_GREEN = 2067276  # 1F8B4C
    BLUE = 3447003  # 3498DB
    DARK_BLUE = 2123412  # 206694
    PURPLE = 10181046  # 9B59B6
    DARK_PURPLE = 7419530  # 71368A
    LUMINOUS_VIVID_PINK = 15277667  # E91E63
    DARK_VIVID_PINK = 11342935  # AD1457
    GOLD = 15844367  # F1C40F
    DARK_GOLD = 12745742  # C27C0E
    ORANGE = 15105570  # E67E22
    DARK_ORANGE = 11027200  # A84300
    RED = 15158332  # E74C3C
    DARK_RED = 10038562  # 992D22
    GREY = 9807270  # 95A5A6
    DARK_GREY = 9936031  # 979C9F
    DARKER_GREY = 8359053  # 7F8C8D
    LIGHT_GREY = 12370112  # BCC0C0
    NAVY = 3426654  # 34495E
    DARK_NAVY = 2899536  # 2C3E50
    YELLOW = 16776960  # FFFF00


@dataclasses.dataclass
class User:
    avatar: str
    discriminator: str
    id: str
    public_flags: int
    username: str
    bot: bool = False


@dataclasses.dataclass
class Member:  # pylint: disable=too-many-instance-attributes
    deaf: bool
    is_pending: bool
    joined_at: dataclasses.InitVar[datetime.datetime]
    mute: bool
    nick: t.Optional[str]
    pending: bool
    roles: t.List[str]
    user: dataclasses.InitVar[User]
    permissions: str = ""
    premium_since: str = ""
    avatar: str = ""
    communication_disabled_until: str = ""
    flags: str = ""

    def __post_init__(self, joined_at, user):
        self.user = User(**user)
        self.joined_at = dateutil.parser.parse(joined_at)

    def __str__(self) -> str:
        return self.nick or self.user.username


@dataclasses.dataclass
class Interaction:  # pylint: disable=too-many-instance-attributes
    @enum.unique
    class Type(enum.Enum):
        PING = 1
        APPLICATION_COMMAND = 2

    @enum.unique
    class ResponseType(enum.Enum):
        PONG = 1
        CHANNEL_MESSAGE_WITH_SOURCE = 4
        DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5

    application_id: str
    channel_id: str
    data: t.Dict
    guild_id: str
    id: str
    member: dataclasses.InitVar[Member]
    token: str
    type: dataclasses.InitVar[Type]
    version: str
    guild_locale: str
    locale: str

    def __post_init__(self, member, type_):
        self.member = Member(**member)
        self.type = Interaction.Type(type_)


@dataclasses.dataclass
class Role:  # pylint: disable=too-many-instance-attributes
    id: str
    name: str
    color: int
    hoist: bool
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    unicode_emoji: str
    icon: str
    tags: t.Optional[t.List] = None

    def __str__(self) -> str:
        return f"<@&{self.id}>"
