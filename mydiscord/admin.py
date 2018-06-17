"""
Discord-related admin.
"""
from django.contrib import admin

# Register your models here.
from mydiscord.models import Guild, Module, Alias

admin.site.register(Guild, admin.ModelAdmin)
admin.site.register(Module, admin.ModelAdmin)


class AliasAdmin(admin.ModelAdmin):
    list_display = ['guild', 'source', 'target']
    list_filter = ['guild']


admin.site.register(Alias, AliasAdmin)
