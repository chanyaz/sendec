from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.shortcuts import render_to_response, render, HttpResponseRedirect
from django.db.models import Q


from news.models import NewsWatches, News


#   @login_required(login_url="/auth/login/")
def render_search_page(request):
    args = {
        "latest_news": get_latest_news_total(request),
    }

    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)


    if "q" in request.GET and request.GET["q"]:
        search_word = request.GET["q"]
        if search_word is "":
            args["erorr_empty_field"] = True
        elif len(get_search_result_text(request, search_word)) < 1 and len(get_search_result_text(request, search_word)) < 1\
                and len(get_search_among_users(request, search_word)) < 1 and len(get_company(request, search_word)) < 1:
            args["empty_result"] = True
            args["popular_news"] = get_popular_news(request)
        else:
            args["results"] = get_search_result(request, search_word)
            args["matches_amount"] = get_matches_amount(request, search_word)
            args["users_matches"] = get_search_among_users(request, search_word).values()
            args["companies_matches"] = get_company(request, search_word).values()

        args["search_word"] = search_word
    args.update(csrf(request))
    return render_to_response("search.html", args)


def get_latest_news_total(request):
    from news.models import News
    latest_10_news = News.objects.all().order_by("-news_post_date")[:10]
    return latest_10_news


#   @login_required(login_url="/auth/login/")
def get_search_result(request, search_word):
    from news.models import News, NewsPortal
    return News.objects.filter(Q(news_title__contains=search_word) | Q(news_post_text__contains=search_word) | Q(news_portal_name_id=NewsPortal.objects.get(portal_name=search_word).id)).values()


#   @login_required(login_url="/auth/login/")
def get_search_result_text(request, search_word):
    from news.models import News
    return News.objects.filter(news_post_text__contains=search_word).order_by("-news_post_date").values()


#   @login_required(login_url="/auth/login/")
def get_matches_amount(request, search_word):
    from news.models import News
    news = News.objects.filter(Q(news_title__contains=search_word) | Q(news_post_text__contains=search_word)).count()
    users = get_search_among_users(request, search_word).count()
    companies = get_company(request, search_word).count()
    return news + users + companies


def get_popular_news(request):
    popular_news_id_list = NewsWatches.objects.all().order_by("watches")[:10].values("news_id")
    news_list = []
    for i in popular_news_id_list:
        news_list.append(News.objects.get(id=int(i["news_id"])))
    return news_list


def get_search_among_users(request, search_word):
    return User.objects.filter(Q(username__contains=search_word))


def get_company(request, search_word):
    from news.models import Companies
    return Companies.objects.filter(Q(name__contains=search_word))