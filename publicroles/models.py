# Create your models here.
from django.db import models

from mydiscord.models import Guild


class PublicRole(models.Model):
    uid = models.CharField(max_length=32, unique=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE,
                              related_name='public_roles')
