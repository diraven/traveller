"""
Publicroles admin.
"""

# Register your models here.
from django.contrib import admin

from publicroles.models import PublicRole


class PublicRoleAdmin(admin.ModelAdmin):
    list_display = ['discord_id', 'guild']
    list_filter = ['guild']


admin.site.register(PublicRole, PublicRoleAdmin)
