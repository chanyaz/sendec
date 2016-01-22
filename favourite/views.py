from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from django.shortcuts import render_to_response
from userprofile.models import UserLikesNews
from news.models import RssNews
from .models import RssSaveNews



@login_required(login_url="/auth/login/")
def render_liked_news_page(request):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    args = {
        "username": User.objects.get(username=auth.get_user(request).username),
        "favs": get_favourite_news(request, user_instance),
        "fav_len": get_favourite_news(request, user_instance).count(),
    }
    args.update(csrf(request))
    return render_to_response("liked_news.html", args)


def get_favourite_news(request, user):
    return RssSaveNews.objects.filter(user_id=user.id).values()


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

