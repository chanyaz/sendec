from django.contrib import admin
from .models import RssSaveNews


class RssSaveNewsAdmin(admin.ModelAdmin):
    model = RssSaveNews

admin.site.register(RssSaveNews, RssSaveNewsAdmin)
