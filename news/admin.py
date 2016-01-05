from django import forms
from django.contrib import admin
from .models import News, NewsPortal, NewsCategory, Companies, RssNews, RssPortals, TopVideoContent, TopNews
from ckeditor.widgets import CKEditorWidget


class RssNewsAdmin(admin.ModelAdmin):
    model = RssNews
    list_display = ['title', 'portal_name', 'category']#, 'get_category', 'get_author')

    def get_portal(self, obj):
        return obj.portal_name.portal



admin.site.register(TopVideoContent)
# admin.site.register(RssPortals)
admin.site.register(NewsCategory)
admin.site.register(NewsPortal)
#admin.site.register(News)


class PostAdminTopNewsForm(forms.ModelForm):
    top_news_post_text_english = forms.CharField(widget=CKEditorWidget(), required=False)
    top_news_post_text_russian = forms.CharField(widget=CKEditorWidget(), required=False)
    top_news_post_text_chinese = forms.CharField(widget=CKEditorWidget(), required=False)
    class Meta:
        model = TopNews
        fields = "__all__"


class PostAdminTopNews(admin.ModelAdmin):
    form = PostAdminTopNewsForm


class PostAdminForm(forms.ModelForm):
    news_post_text_english = forms.CharField(widget=CKEditorWidget(), required=False)
    news_post_text_russian = forms.CharField(widget=CKEditorWidget(), required=False)
    news_post_text_chinese = forms.CharField(widget=CKEditorWidget(), required=False)
    class Meta:
        model = News
        fields = "__all__"


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm


class RssPortalsForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), required=False, label="Description(Max. length - 1024)")
    class Meta:
        model = RssPortals
        fields = "__all__"


class RssPortalsAdminForm(admin.ModelAdmin):
    form = RssPortalsForm


class CompaniesEditorFormAdmin(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Companies
        fields = "__all__"


class AompaniesEditorAdmin(admin.ModelAdmin):
    form = CompaniesEditorFormAdmin

admin.site.register(RssPortals, RssPortalsAdminForm)
admin.site.register(TopNews, PostAdminTopNews)
admin.site.register(News, PostAdmin)
admin.site.register(Companies, AompaniesEditorAdmin)
admin.site.register(RssNews, RssNewsAdmin)
