from django import template
from django.utils.importlib import import_module
from django.contrib.auth.models import User


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

@register.filter(name="check_reading_category")
def check_reading_category(value_cid, value_username):
    from news.models import NewsCategory, News
    from userprofile.models import UserSettings
    user_settings_categories = UserSettings.objects.get(user_id=User.objects.get(username=value_username).id).categories_to_show.split(",")
    if str(value_cid) in user_settings_categories:
        return True
    else:
        return False

@register.filter(name="get_article_author")
def get_article_author(value):
    from django.contrib.auth.models import User
    first_name = User.objects.get(id=value).first_name
    second_name = User.objects.get(id=value).last_name
    return first_name.capitalize()+" "+second_name.capitalize()

@register.filter(name="get_portal_name")
def get_portal_name(value):
    from news.models import NewsPortal
    return NewsPortal.objects.get(id=int(value)).portal_name

@register.filter(name="get_rss_portal_name")
def get_rss_portal_name(value):
    from news.models import RssPortals
    return RssPortals.objects.get(id=int(value)).portal


@register.filter(name="get_user_photo")
def get_user_photo(value):
    return User.objects.get(id=int(value)).profile.user_photo