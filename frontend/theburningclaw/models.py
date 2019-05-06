from django.core.validators import MinValueValidator
from django.db import models


class ThingKind(models.Model):
    slug = models.CharField(max_length='64', unique=True)
    title = models.CharField(max_length='64', unique=True)


class Thing(models.Model):
    kind = models.ForeignKey(ThingKind, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(
        validators=(MinValueValidator(1),),
        default=1,
    )
