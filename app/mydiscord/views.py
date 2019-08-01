"""Mydiscord views."""

# Create your views here.
from rest_framework import viewsets

from mydiscord.models import Alias
from mydiscord.serializers import AliasSerializer


class AliasViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited."""

    queryset = Alias.objects.all()
    serializer_class = AliasSerializer

    def get_queryset(self):
        """Get alias queryset, limit results to the respective guild."""
        guild_discord_id = self.request.query_params.get(
            'guild_discord_id',
            None,
        )
        source = self.request.query_params.get(
            'source',
            None,
        )
        return self.queryset.filter(
            guild__discord_id=guild_discord_id,
            source=source,
        )
