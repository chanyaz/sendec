from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from django.shortcuts import render_to_response, RequestContext
from userprofile.models import UserLikesNews
from news.models import RssNews
from .models import RssSaveNews
from news.views import get_user_rss_portals



@login_required(login_url="/auth/login/")
def render_liked_news_page(request, template="liked_news.html", fav_template="fav_template.html", extra_context=None):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    args = {
        "username": User.objects.get(username=auth.get_user(request).username),
        "favs": list(get_favourite_news(request, user_instance)),
        "fav_template": fav_template,
        "user_rss_portals": get_user_rss_portals(request, user_id=user_instance.id),
        "here_private": True,
    }
    if request.is_ajax():
        template = fav_template
    args.update(csrf(request))
    response = render_to_response(template, context=args, context_instance=RequestContext(request))
    return response


def get_favourite_news(request, user):
    translation = {
        "id": "id",
        "title": "title",
        "date_posted": "date_posted",
        "portal_name_id": "portal_name_id",
        "author_id": "author_id"
    }
    instance = RssSaveNews.objects.raw("SELECT n.id, n.title, n.date_posted, n.portal_name_id, n.author FROM news_rss n "
                                       "INNER JOIN rss_save r ON r.rss_id=n.id and r.user_id=%s" % user.id, translations=translation)
    #return RssSaveNews.objects.filter(user_id=user.id).values()
    return instance


def add_fav(request, news_id):
    user = User.objects.get(username=auth.get_user(request).username)
    # if not RssSaveNews.objects.filter(user_id=user.id).filter(rss_id=news_id).exists():
    RssSaveNews.objects.create(
        user_id=user.id,
        rss_id=news_id,
    )
    # else:
    #     pass
    return HttpResponse()

