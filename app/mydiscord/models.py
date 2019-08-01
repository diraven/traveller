"""Discord models module."""
from django.db import models


class Module(models.Model):
    """Discord commands module."""

    name = models.CharField(max_length=16, unique=True)  # typing: ignore

    def __str__(self) -> str:
        """Crabot module string representation."""
        return self.name


class Guild(models.Model):
    """Discord guild."""

    discord_id = models.BigIntegerField(unique=True)
    trigger = models.CharField(max_length=1, default='.')
    modules = models.ManyToManyField(Module, related_name='guilds', blank=True)

    def __str__(self) -> str:
        """Crabot guild string representation."""
        return str(self.discord_id)


class Alias(models.Model):
    """Discord per-guild command alias."""

    guild = models.ForeignKey(Guild, on_delete=models.CASCADE,
                              related_name='aliases')
    source = models.CharField(max_length=16)
    target = models.CharField(max_length=64)

    class Meta:
        """Crabot alias meta."""

        unique_together = (
            ('guild', 'source'),
        )

    def __str__(self) -> str:
        """Crabot alias string representation."""
        return '{}->{}'.format(self.source, self.target)
