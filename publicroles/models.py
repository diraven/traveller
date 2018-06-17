# Create your models here.
from django.db import models

from mydiscord.models import Guild


class PublicRole(models.Model):
    uid = models.IntegerField(unique=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE,
                              related_name='public_roles')
