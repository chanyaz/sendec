# -*-coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import render_to_response, render
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.contrib.auth.models import User

from django.contrib.admin.views.decorators import staff_member_required

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

    if User.objects.get(username=auth.get_user(request).username).is_active:
        return render_to_response("index.html", args)
    else:
        return HttpResponseRedirect("/auth/preferences=categories")


def render_news_politics(request):
    return News.objects.filter(news_category_id=NewsCategory.objects.get(category_name="Politics").id)

def get_latest_news_total(request):
    latest_10_news = News.objects.all().order_by("-news_post_date")[:10]
    return latest_10_news


@login_required(login_url='/auth/login/')
def render_current_news(request, category_id, news_id):
    import datetime
    from userprofile.models import UserLikesNews
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
        "replies_total": replies_load(request, news_id),
        "liked": check_like(request, news_id),
        "disliked": check_dislike(request, news_id),
        "like_amount": UserLikesNews.objects.filter(news_id=news_id).filter(like=True).count(),
        "dislike_amount": UserLikesNews.objects.filter(news_id=news_id).filter(dislike=True).count(),
        "current_news_title": News.objects.get(id=news_id).news_title,
    }
    addition_news_watches(request, news_id)
    args.update(csrf(request))
    return render_to_response("current_news.html", args)


@login_required(login_url="/auth/login/")
def render_user_news(request):
    args = {
        "title": "| My news",
        "username": auth.get_user(request).username,
        "usernews": get_user_news_by_portals(request),
        "deftest": test(request),
    }
    args.update(csrf(request))
    return render_to_response("user_news.html", args)


@login_required(login_url="/auth/login/")
def render_top_news_page(request):
    from .models import NewsWatches
    args = {
        "username": auth.get_user(request).username,
        "top_news": get_top_news(request),
    }
    args.update(csrf(request))

    return render_to_response("top_news.html", args)


def get_user_news_by_portals(request):
    from news.models import News, NewsPortal
    from userprofile.models import UserSettings
    from itertools import chain
    from operator import attrgetter
    from django.db.models import Q

    inst = UserSettings.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id).portals_to_show.split(",")

    #total_news = sorted(
    #    chain(
    #        News.objects.filter(news_portal_name_id=inst[cur_id]).values() for cur_id in range(len(inst)-1)
    #    ),
    #    key=attrgetter("news_post_date"),
    #    reverse=True
    #)

    total_news_2 = list(News.objects.filter(Q(news_portal_name_id=inst[cur_id])).order_by("-news_post_date") for cur_id in range(len(inst)-1))

    return total_news_2



def test(request):
    from news.models import News, NewsPortal
    from userprofile.models import UserSettings
    from itertools import chain
    from operator import attrgetter
    from django.db.models import Q

    inst_portals = UserSettings.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id).portals_to_show.split(",")
    inst_categories = UserSettings.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id).categories_to_show.split(",")

    # return chain(
    #         [News.objects.filter(Q(news_portal_name_id=inst_portals[cur_id])) for cur_id in range(len(inst_portals)-1)],
    #         [News.objects.filter(Q(news_category_id=inst_categories[cur_id])) for cur_id in range(len(inst_categories)-1)],
    #     (News.objects.order_by("-news_post_date"))
    #     )

    check = False

    test_new = sorted(
        chain(
            News.objects.filter(news_category_id=1),
            News.objects.filter(news_category_id=6 if check == True else 0),
        ),
        key=attrgetter("news_post_date"),
        reverse=True
    )
    return test_new
    #return [News.objects.filter(Q(news_category_id=inst_categories[cur_cat_id])).filter(Q(news_portal_name_id=inst_portals[cur_id]))
     #       for cur_cat_id in range(len(inst_categories)-1) for cur_id in range(len(inst_portals)-1)]



def check_like(request, news_id):
    from userprofile.models import UserLikesNews
    if UserLikesNews.objects.filter(user_id=User.objects.get(username=auth.get_user(request).username).id).filter(news_id=news_id).filter(like=True).exists():
        return True
    else:
        return False


def check_dislike(request, news_id):
    from userprofile.models import UserLikesNews
    if UserLikesNews.objects.filter(user_id=User.objects.get(username=auth.get_user(request).username).id).filter(news_id=news_id).filter(dislike=True  ).exists():
        return True
    else:
        return False


def update_latest_news(request):
    from .models import News
    import json

    latest_new = News.objects.filter(news_latest_shown=False).order_by("-news_post_date")[0]
    string = """<span class='time' style='color: blue;'>%s</span>
<span class='title' onclick="location.href='/news/%s/%s/';">%s</span><br>""" \
             % (latest_new.news_post_date.time().strftime("%H:%M"), latest_new.news_category_id, latest_new.id, latest_new.news_title)

    response_data = {
        "latest_news": [cur_new.get_json_news() for cur_new in News.objects.all().all().order_by("-news_post_date")[:1]],
        "string": [string]
    }

    latest_10 = News.objects.filter(news_currently_showing=True).order_by("-news_post_date")[:10]
    latest_10[10].news_currently_showing = False
    latest_10[10].save()

    latest_new.news_currently_showing = True
    latest_new.news_latest_shown = True
    latest_new.save()
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def set_shown(request, news_id):
    from .models import News
    instance = News.objects.get(id=int(news_id))
    instance.news_latest_shown = True
    instance.save()
    return HttpResponse()


@login_required(login_url="/auth/login/")
def addition_news_watches(request, news_id):
    from .models import NewsWatches
    if NewsWatches.objects.filter(news_id=news_id).exists():
        instance = NewsWatches.objects.get(news_id=news_id)
        instance.watches += 1
        instance.save()
    else:
        NewsWatches.objects.create(
            news_id=news_id,
            watches=1,
        )
    return HttpResponse()


def get_top_news(request):
    """
    Get top 10 by watches news.
    :param request:
    :return:
    """
    from .models import NewsWatches, News
    top_list_id = NewsWatches.objects.all()[:10].values()
    top_news = [News.objects.get(id=int(cur_news_id["news_id"])) for cur_news_id in top_list_id]
    return top_news


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
        "latest_news": get_latest_news_total(request),
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
    from userprofile.models import UserLikesNews
    import json
    if UserLikesNews.objects.filter(user_id=User.objects.get(username=auth.get_user(request).username).id).filter(news_id=news_id).exists():
        user_like_instance = UserLikesNews.objects.filter(user_id=User.objects.get(username=auth.get_user(request).username).id).get(news_id=news_id)
        # Add like to pair USER-news
        user_like_instance.dislike=False
        user_like_instance.like=True
        user_like_instance.save()
    else:
        instance = News.objects.get(id=news_id)
        instance.news_likes += 1
        instance.save()
        UserLikesNews.objects.create(
            like=True,
            dislike=False,
            news_id=news_id,
            user_id=User.objects.get(username=auth.get_user(request).username).id
        )
    return HttpResponse()


@login_required(login_url="/auth/login/")
def add_dislike_news(request, news_id):
    from .models import News
    from userprofile.models import UserLikesNews
    import json

    if UserLikesNews.objects.filter(user_id=User.objects.get(username=auth.get_user(request).username).id).filter(news_id=news_id).exists():
        user_dislike_instance = UserLikesNews.objects.filter(user_id=User.objects.get(username=auth.get_user(request).username).id).get(news_id=news_id)
        # Add like to pair USER-news
        user_dislike_instance.dislike=True
        user_dislike_instance.like=False
        user_dislike_instance.save()
    else:
        instance = News.objects.get(id=news_id)
        instance.news_likes += 1
        instance.save()
        UserLikesNews.objects.create(
            like=False,
            dislike=True,
            news_id=news_id,
            user_id=User.objects.get(username=auth.get_user(request).username).id
        )
    return HttpResponse()


@login_required(login_url="/auth/login/")
def check_like_amount(request, news_id):
    from userprofile.models import UserLikesNews
    import json
    return HttpResponse(json.dumps({"likes": UserLikesNews.objects.filter(news_id=news_id).filter(like=True).count()}), content_type="application/json")


@login_required(login_url="/auth/login/")
def check_dislike_amount(request, news_id):
    from userprofile.models import UserLikesNews
    import json
    return HttpResponse(json.dumps({"dislikes": UserLikesNews.objects.filter(news_id=news_id).filter(dislike=True).count()}), content_type="application/json")


def delete_comment(request, comment_id):
    from news.models import NewsComments
    args = {}
    args.update(csrf(request))
    news_instance = News.objects.get(id=NewsComments.objects.get(id=int(comment_id)).news_attached_id)
    if User.objects.get(username=auth.get_user(request).username).is_staff:
        instance = NewsComments.objects.get(id=int(comment_id))
        instance.delete()
    else:
        pass
    return HttpResponseRedirect("/news/%s/%s/" % (news_instance.news_category_id, news_instance.id), args)

def delete_reply(request, reply_id):
    from news.models import NewsCommentsReplies
    args = {}
    args.update(csrf(request))
    news_instance = News.objects.get(id=NewsCommentsReplies.objects.get(id=int(reply_id)).news_attached_id)
    if User.objects.get(username=auth.get_user(request).username).is_staff:
        instance = NewsCommentsReplies.objects.get(id=int(reply_id))
        instance.delete()
    else:
        pass
    return HttpResponseRedirect("/news/%s/%s/" % (news_instance.news_category_id, news_instance.id), args)