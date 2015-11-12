from django.contrib import admin
from .models import UserSettings


class UserSettingsAdmin(admin.ModelAdmin):
    inlines = []
    list_display = ["user", "color_scheme"]


admin.site.register(UserSettings, UserSettingsAdmin)