"""
Discord models module.
"""
from django.db import models


class Module(models.Model):
    """
    Discord commands module.
    """
    name = models.CharField(max_length=16, unique=True)

    def __str__(self) -> str:
        return self.name


class Guild(models.Model):
    """
    Discord guild.
    """
    uid = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=32, unique=True)
    modules = models.ManyToManyField(Module, related_name="guilds", blank=True)

    def __str__(self) -> str:
        return self.name


class Alias(models.Model):
    """
    Discord per-guild command alias.
    """
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE,
                              related_name='aliases')
    source = models.CharField(max_length=16)
    target = models.CharField(max_length=16)

    def __str__(self) -> str:
        return "{}->{}".format(self.source, self.target)
