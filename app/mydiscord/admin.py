"""Discord-related admin."""
from django.contrib import admin

# Register your models here.
from mydiscord.models import Guild, Alias

admin.site.register(Guild, admin.ModelAdmin)


class AliasAdmin(admin.ModelAdmin):
    """Command alias admin."""

    list_display = ['source', 'target', 'guild']
    list_filter = ['guild']


admin.site.register(Alias, AliasAdmin)
