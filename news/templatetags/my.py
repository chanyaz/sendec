from django import template
from django.utils.importlib import import_module


register = template.Library()


@register.filter(name="get_username")
def get_username(value):
    from userprofile.models import User
    return User.objects.get(id=int(value)).username

@register.filter(name="get_news_title")
def get_news_title(value):
    from news.models import News
    return News.objects.get(id=int(value)).news_title


@register.filter(name="get_news_text")
def get_news_text(value):
    from news.models import News
    return News.objects.get(id=int(value)).news_post_text


@register.filter(name="get_news_date")
def get_news_date(value):
    from news.models import News
    return News.objects.get(id=int(value)).news_post_date


@register.filter(name="get_news_portal")
def get_news_portal(value):
    from news.models import News, NewsPortal
    return NewsPortal.objects.get(id=News.objects.get(id=int(value)).news_portal_name_id).portal_name


@register.filter(name="get_news_category")
def get_news_category(value, get_id=False):
    from news.models import News, NewsCategory
    if get_id == False:
        return NewsCategory.objects.get(id=News.objects.get(id=int(value)).news_category_id).category_name
    else:
        return News.objects.get(id=int(value)).news_category_id
