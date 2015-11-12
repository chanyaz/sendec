from django.shortcuts import render
from django.shortcuts import render_to_response, render
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

from .models import News, NewsPortal, NewsCategory


@login_required(login_url='/auth/login/')
def main_page_load(request):
    args = {
        "title": "| Home",
        "news_block": True,
        "username": auth.get_user(request).username,
        "total_politics": render_news_politics(request),
    }
    args.update(csrf(request))

    return render_to_response("index.html", args)

def render_news_politics(request):
    return News.objects.filter(news_category_id=NewsCategory.objects.get(category_name="Politics").id)

def get_latest_news_total(request):
    return News.objects.all().order_by("-news_post_date")[:10]


@login_required(login_url='/auth/login/')
def render_current_news(request, category_id, news_id):
    import datetime
    from .forms import NewsCommentsForm, NewsCommentsRepliesForm
    args = {
        "title": "| %s" % News.objects.get(id=news_id).news_title,
        "username": auth.get_user(request).username,
        "current_news_values": News.objects.get(id=news_id),
        "other_materials": render_news_politics(request).exclude(id=news_id)[:12],
        "latest_news": get_latest_news_total(request),
        "current_day": datetime.datetime.now().day,
        "comments_form": NewsCommentsForm,
        "replies_form": NewsCommentsRepliesForm,
        "comments_total": comments_load(request, news_id),
        "replies_total": replies_load(request, news_id)
    }
    args.update(csrf(request))

    return render_to_response("current_news.html", args)


@login_required(login_url="/auth/login/")
def render_current_news_comments(request, category_id, news_id):
    from .models import NewsComments, NewsCommentsReplies
    import json

    news_comments = NewsComments.objects.filter(news_attached=int(news_id))
    news_replies = NewsCommentsReplies.objects.filter(news_attached=int(news_id))


    response_data = {
        "content_comments": [data_comments.get_json_comments() for data_comments in news_comments.all()],
        "content_replies": [data_replies.get_json_replies() for data_replies in news_replies.all()]
    }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required(login_url="/auth/login/")
def render_current_category(request, category_name):
    args = {
        "title": "| Politics",
        "username": auth.get_user(request).username,
        "category_title": category_name.capitalize(),
        "cat_news": News.objects.filter(news_category_id=NewsCategory.objects.get(category_name=category_name.capitalize()).id),
    }
    args.update(csrf(request))


    return render_to_response("current_category.html", args)


@login_required(login_url="/auth/login")
def comment_send(request, category_id, news_id):
    from .forms import NewsCommentsForm
    from userprofile.models import UserProfile
    args = {
        "username": auth.get_user(request).username,

    }
    args.update(csrf(request))


    if request.POST:
        form = NewsCommentsForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news_attached = News.objects.get(id=news_id)
            comment.comments_author = User.objects.get(username=auth.get_user(request).username)
            form.save()

    return HttpResponseRedirect("/news/%s/%s/" % (category_id, news_id), args)

def comments_load(request, news_id):
    from .models import NewsComments
    return NewsComments.objects.filter(news_attached=news_id).order_by("-comments_post_date").values()

@login_required(login_url="/auth/login/")
def reply_send(request, news_id, comment_id):
    from .forms import NewsCommentsRepliesForm
    from .models import NewsComments
    args = {
        "username": auth.get_user(request).username,
    }
    args.update(csrf(request))

    if request.POST:
        form = NewsCommentsRepliesForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment_attached = NewsComments.objects.get(id=comment_id)
            reply.news_attached = News.objects.get(id=news_id)
            reply.reply_author = User.objects.get(username=auth.get_user(request).username)
            form.save()
    return HttpResponseRedirect("/news/%s/%s/" % (News.objects.get(id=news_id).news_category_id,news_id), args)


def replies_load(request, news_id):
    from .models import NewsCommentsReplies
    return NewsCommentsReplies.objects.filter(news_attached=news_id).order_by("reply_post_date").values()

@login_required(login_url="/auth/login/")
def add_like_news(request, news_id):
    from .models import News
    import json
    instance = News.objects.get(id=news_id)
    instance.news_likes += 1
    instance.save()
    return HttpResponse()

@login_required(login_url="/auth/login/")
def check_like_amount(request, news_id):
    from .models import News
    import json
    return HttpResponse(json.dumps({"likes": News.objects.get(id=int(news_id)).news_likes}), content_type="application/json")

@login_required(login_url="/auth/login/")
def add_dislike_news(request, news_id):
    from .models import News
    import json
    instance = News.objects.get(id=news_id)
    instance.news_dislikes += 1
    instance.save()
    return HttpResponse()

@login_required(login_url="/auth/login/")
def check_dislike_amount(request, news_id):
    from .models import News
    import json
    return HttpResponse(json.dumps({"dislikes": News.objects.get(id=int(news_id)).news_dislikes}), content_type="application/json")
