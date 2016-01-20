from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.shortcuts import render_to_response
from news.models import News


@login_required(login_url="/auth/login/")
def render_notify_page(request):
    args = {
        "username": User.objects.get(username=auth.get_user(request).username),
    }
    args.update(csrf(request))

    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response("notify.html", args)


def get_news_for_footer(request):
    return News.objects.order_by("-news_post_date").defer("news_dislikes").defer("news_likes").defer("news_post_text_english").defer("news_post_text_chinese").defer("news_post_text_russian").defer("news_author").defer("news_portal_name")
