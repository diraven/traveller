import typing

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, IntegrityError
from django.db.models import F


class Character(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)

    def give(
            self,
            *things: typing.List[typing.Tuple['ThingKind', int]],
    ):
        for thing_kind, count in things:
            try:
                Thing(
                    owner=self,
                    kind=thing_kind,
                    count=count,
                ).save()
            except IntegrityError:
                self.thing_set.filter(
                    kind=thing_kind,
                ).update(count=F('count') + count)

    def __str__(self):
        """As string."""
        return self.name


class ThingKind(models.Model):
    slug = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        """As string."""
        return self.name


class Thing(models.Model):
    owner = models.ForeignKey(Character, on_delete=models.CASCADE)
    kind = models.ForeignKey(ThingKind, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(
        validators=(MinValueValidator(1),),
        default=1,
    )

    def __str__(self):
        """As string."""
        return f'{self.kind} x {self.count}'

    class Meta:
        unique_together = (
            ('owner', 'kind'),
        )


class Lootable(models.Model):
    venture = models.ForeignKey('Venture', on_delete=models.CASCADE)
    thing_kind = models.ForeignKey(ThingKind, on_delete=models.CASCADE)
    chance = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1),
        ],
    )
    count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    count_deviation = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.thing_kind.name} ' \
            f'{self.count - self.count_deviation}-' \
            f'{self.count + self.count_deviation} ' \
            f'({self.chance * 100}%)'

    class Meta:
        unique_together = (
            ('venture', 'thing_kind'),
        )


class Venture(models.Model):
    slug = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64, unique=True)

    lootables = models.ManyToManyField(ThingKind, through=Lootable)

    def __str__(self):
        """As string."""
        return self.name
