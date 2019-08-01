"""Mydiscord module serializers."""
from rest_framework import serializers

from mydiscord.models import Alias


class AliasSerializer(serializers.HyperlinkedModelSerializer):
    """Alias serializer."""

    class Meta:
        """Alias serializer meta."""

        model = Alias
        fields = (
            'source',
            'target',
        )
