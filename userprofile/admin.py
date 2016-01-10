from django.contrib import admin
from .models import UserSettings, UserRssPortals, ModeratorSpecialFields


class UserSettingsAdmin(admin.ModelAdmin):
    inlines = []
    list_display = ["user", "color_scheme"]


class UserRssPortalsAdmin(admin.ModelAdmin):
    model = UserRssPortals
    list_display = ['portal', 'user', 'check',]#, 'get_category', 'get_author')

    list_filter = ['portal', 'user', 'check',]



admin.site.register(UserRssPortals, UserRssPortalsAdmin)

admin.site.register(UserSettings, UserSettingsAdmin)
admin.site.register(ModeratorSpecialFields)

