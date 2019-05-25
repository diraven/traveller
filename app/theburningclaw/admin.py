from django.contrib import admin

# Register your models here.
from theburningclaw.models import Character, ThingKind

admin.site.register(ThingKind)
admin.site.register(Character)
