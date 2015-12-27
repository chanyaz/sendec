from django import forms
from django.contrib import admin
from .models import News, NewsPortal, NewsCategory, Companies, RssNews, RssPortals, TopVideoContent
from ckeditor.widgets import CKEditorWidget


#admin.site.register(Companies)


admin.site.register(TopVideoContent)
admin.site.register(RssNews)
admin.site.register(RssPortals)
admin.site.register(NewsCategory)
admin.site.register(NewsPortal)
#admin.site.register(News)


class PostAdminForm(forms.ModelForm):
    news_post_text_english = forms.CharField(widget=CKEditorWidget(), required=False)
    news_post_text_russian = forms.CharField(widget=CKEditorWidget(), required=False)
    news_post_text_chinese = forms.CharField(widget=CKEditorWidget(), required=False)
    class Meta:
        model = News
        fields = "__all__"


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm


class CompaniesEditorFormAdmin(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Companies
        fields = "__all__"

class AompaniesEditorAdmin(admin.ModelAdmin):
    form = CompaniesEditorFormAdmin


admin.site.register(News, PostAdmin)
admin.site.register(Companies, AompaniesEditorAdmin)
