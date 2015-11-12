from django.contrib import admin
from .models import News, NewsPortal, NewsCategory


# Register your models here.
admin.site.register(NewsCategory)
admin.site.register(NewsPortal)
admin.site.register(News)
