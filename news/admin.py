from django import forms
from django.contrib import admin
from .models import News, NewsPortal, NewsCategory

# Register your models here.
admin.site.register(NewsCategory)
admin.site.register(NewsPortal)
#admin.s# ite.register(News)

from ckeditor.widgets import CKEditorWidget


class PostAdminForm(forms.ModelForm):
    news_post_text = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = News
        fields = "__all__"


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm

admin.site.register(News, PostAdmin)