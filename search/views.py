from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.shortcuts import render_to_response, render, HttpResponseRedirect
from django.db.models import Q

# Create your views here.

@login_required(login_url="/auth/login/")
def render_search_page(request):
    args = {
        "username": User.objects.get(username=auth.get_user(request).username),
    }

    if "q" in request.GET and request.GET["q"]:
        search_word = request.GET["q"]
        if search_word is "":
            args["erorr_empty_field"] = True
        elif len(get_search_result_text(request,search_word)) < 1 and len(get_search_result_titles(request, search_word)) < 1:
            args["empty_result"] = True
        else:
            args["results"] = get_search_result(request, search_word)
            args["among_text"] = get_search_result_text(request, search_word)

    args.update(csrf(request))
    return render_to_response("search.html", args)

@login_required(login_url="/auth/login/")
def get_search_result(request, search_word):
    from news.models import News
    return News.objects.filter(Q(news_title__contains=search_word) | Q(news_post_text__contains=search_word)).values()


@login_required(login_url="/auth/login/")
def get_search_result_text(request, search_word):
    from news.models import News
    return News.objects.filter(news_post_text__contains=search_word).order_by("-news_post_date").values()