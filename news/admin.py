from django import forms
from django.contrib import admin
from .models import News, NewsPortal, NewsCategory, Companies, RssNews, RssPortals, TopVideoContent, TopNews, \
    NewsWatches, UserRssNewsReading, RSSChannels,RssNewsCovers
from ckeditor.widgets import CKEditorWidget


class RssNewsAdmin(admin.ModelAdmin):
    model = RssNews
    list_display = ['title', 'portal_name', 'category']#, 'get_category', 'get_author')
    list_filter = ["portal_name", "category"]


    def get_portal(self, obj):
        return obj.portal_name.portal


class NewsWatchesAdmin(admin.ModelAdmin):
    model = NewsWatches
    list_display = ['news', 'watches']
    list_filter = ['watches']


admin.site.register(NewsWatches, NewsWatchesAdmin)
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
    prepopulated_fields = {'slug': ('top_news_title_english', )}


class RSSNewsAdminForm(forms.ModelForm):
    post_text = forms.CharField(widget=CKEditorWidget(), required=False)
    content_value = forms.CharField(widget=CKEditorWidget(), required=False)
    class Meta:
        model = RssNews
        fields = "__all__"



class RSSAdmin(admin.ModelAdmin):
    form = RSSNewsAdminForm
    list_filter = ["category", "author", "portal_name"]


class PostAdminForm(forms.ModelForm):
    news_post_text_english = forms.CharField(widget=CKEditorWidget(), required=False)
    news_post_text_russian = forms.CharField(widget=CKEditorWidget(), required=False)
    news_post_text_chinese = forms.CharField(widget=CKEditorWidget(), required=False)
    class Meta:
        model = News
        fields = "__all__"


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    prepopulated_fields = {'slug': ('news_title_english', )}
    list_display = ['news_title_english', 'news_title_russian', 'news_title_chinese', 'news_category',
                    'news_portal_name', 'news_company_owner', 'news_author',  'news_likes', 'news_dislikes',
                    'news_post_date',]
    list_filter = ['news_category', 'news_portal_name', 'news_company_owner', 'news_author',]


class RssPortalsForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), required=False, label="Description(Max. length - 1024)")
    class Meta:
        model = RssPortals
        fields = "__all__"


class RssPortalsAdminForm(admin.ModelAdmin):
    form = RssPortalsForm
    list_filter = ['follows', 'category']
    list_display = ['portal', 'verbose_name', 'follows', 'category',]


class CompaniesEditorFormAdmin(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Companies
        fields = "__all__"


class AompaniesEditorAdmin(admin.ModelAdmin):
    form = CompaniesEditorFormAdmin
    list_display = ['name', 'category', 'site',]
    list_filter = ['name', 'category',]


class RssChannelsAdminForm(forms.ModelForm):
    class Meta:
        model = RSSChannels
        fields = "__all__"


class RssChannelAdmin(admin.ModelAdmin):
    form = RssChannelsAdminForm
    list_display = ['portal', 'link', ]
    list_filter = ['portal', ]


admin.site.register(RssPortals, RssPortalsAdminForm)
admin.site.register(TopNews, PostAdminTopNews)
admin.site.register(News, PostAdmin)
admin.site.register(Companies, AompaniesEditorAdmin)
admin.site.register(RssNews, RSSAdmin)
admin.site.register(UserRssNewsReading)
admin.site.register(RSSChannels, RssChannelAdmin)
admin.site.register(RssNewsCovers)