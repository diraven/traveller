import dataclasses
import typing as t

import discord

import models


@dataclasses.dataclass
class Fields:
    bot: models.Bot = dataclasses.field(init=False)
    guild_id: str
    actor_id: str
    target_id: str
    reason: str

    @classmethod
    def from_embed(cls, embed: discord.Embed) -> "Fields":
        data: t.Dict[str, t.Union[int, str]] = {}
        dataclass_fields = [field.name for field in dataclasses.fields(cls)]
        for field in embed.fields:
            if field.name and field.value and field.name in dataclass_fields:
                data[field.name] = field.value
        return cls(**data)  # type: ignore

    async def to_embed(self, bot: models.Bot) -> discord.Embed:
        ban_guild = bot.get_guild(int(self.guild_id))
        ban_actor = bot.get_user(
            int(self.actor_id),
        ) or await bot.fetch_user(int(self.actor_id))
        ban_target = bot.get_user(
            int(self.target_id),
        ) or await bot.fetch_user(int(self.target_id))
        if ban_guild is None:
            raise RuntimeError("Missing ban_guild.")
        if ban_actor is None:
            raise RuntimeError("Missing ban_actor.")
        if ban_target is None:
            raise RuntimeError("Missing ban_target.")

        embed = discord.Embed(
            title="Новий бан",
            description="Бажаєте відправити цей бан на інші сервери?",
        )
        embed = discord.Embed(
            title=f"Бан на сервері {ban_guild.name}",
        )
        embed.add_field(name="Сервер", value=f"{ban_guild.name}")
        embed.add_field(
            name="Модератор",
            value=f"{ban_actor.display_name} '{ban_actor.name}'",
        )
        embed.add_field(
            name="Забанений",
            value=(
                f"{ban_target.mention} '{ban_target.display_name}' '{ban_target.name}' "
            ),
        )
        if ban_target.avatar:
            embed.set_thumbnail(url=ban_target.avatar.url)

        # Add extra data fields.
        for field in dataclasses.fields(self):
            if field.init:
                embed.add_field(name=field.name, value=getattr(self, field.name))

        return embed
