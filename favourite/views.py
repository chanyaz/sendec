from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.shortcuts import render_to_response, render, HttpResponseRedirect

# Create your views here.

@login_required(login_url="/auth/login/")
def render_liked_news_page(request):
    args = {
        "username": User.objects.get(username=auth.get_user(request).username),
        "favourites": get_favourite_news(request),
        "rss_news": get_rss_liked_news(request),
    }
    args.update(csrf(request))
    if request.COOKIES.get("announce"):
        args["hide"] = False
    else:
        args["hide"] = True
    args["beta_announce"] = """<h5>Currently version is only for <i>beta testing(coursework)</i>. We have hidden/disabled some functions and blocks.
Beta test continues <b>till 21.12.15 17:00 GMT(UTC) +0300</b>
<br>If you found any problems or just want to tell us something else, you can <a href="/about/contacts/">write</a> to us.\
<br>We hope that next version will have localisation and mobile app at least for Android OS.</h5>
"""
    return render_to_response("liked_news.html", args)


def get_favourite_news(request):
    from news.models import News
    from userprofile.models import UserLikesNews
    return UserLikesNews.objects.filter(user_id=User.objects.get(username=auth.get_user(request).username).id).filter(like=True).values("news_id")


def get_rss_liked_news(request):
    from news.models import RssSaveNews, RssNews
    user = User.objects.get(username=auth.get_user(request).username)
    user_rss_list = RssSaveNews.objects.filter(user_id=user.id).values("news_id")
    return RssNews.objects.filter(id__in=user_rss_list).values()