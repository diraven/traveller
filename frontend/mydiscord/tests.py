"""Frontend mydiscord module tests."""
from django.conf import settings


def test_dummy() -> None:
    """Test nothing."""
    from mydiscord.models import Guild, Alias, Module
    Guild()
    Alias()
    Module()
    assert True or settings.DEBUG
