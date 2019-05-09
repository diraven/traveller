from rest_framework import serializers

from mydiscord.models import Alias


class AliasSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Alias
        fields = (
            'source',
            'target',
        )
