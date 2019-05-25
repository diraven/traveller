from django.contrib import admin

# Register your models here.
from theburningclaw.models import Character, ThingKind, Venture, Thing, \
    Lootable


class ThingInlineAdmin(admin.TabularInline):
    model = Thing
    extra = 1


class CharacterAdmin(admin.ModelAdmin):
    inlines = (ThingInlineAdmin,)


admin.site.register(Character, CharacterAdmin)

admin.site.register(ThingKind)


class LootableInlineAdmin(admin.TabularInline):
    model = Lootable
    extra = 1


class VentureAdmin(admin.ModelAdmin):
    inlines = (LootableInlineAdmin,)


admin.site.register(Venture, VentureAdmin)
