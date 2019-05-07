from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Character(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)


class ThingKind(models.Model):
    slug = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64, unique=True)


class Thing(models.Model):
    owner = models.ForeignKey(Character, on_delete=models.CASCADE)
    kind = models.ForeignKey(ThingKind, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(
        validators=(MinValueValidator(1),),
        default=1,
    )
