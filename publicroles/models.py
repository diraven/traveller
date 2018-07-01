# Create your models here.
from django.db import models

from mydiscord.models import Guild


class PublicRole(models.Model):
    uid = models.BigIntegerField(unique=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE,
                              related_name='public_roles')

    def __str__(self) -> str:
        return "{}: {}".format(self.guild, self.uid)
