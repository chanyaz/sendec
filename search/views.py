from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.shortcuts import render_to_response, render, HttpResponseRedirect, HttpResponse
from django.db.models import Q


from news.models import NewsWatches, News
from search.models import UserRequests


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
            args["users_matches"] = get_search_among_users(request, search_word)
            args["companies_matches"] = get_company(request, search_word).values()

        args["search_word"] = search_word

        UserRequests.objects.create(
            user_id=User.objects.get(username=auth.get_user(request).username).id,
            request=search_word
        )

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
    return render_to_response("search.html", args)


def get_latest_news_total(request):
    from news.models import News
    latest_10_news = News.objects.all().order_by("-news_post_date")[:10]
    return latest_10_news


#   @login_required(login_url="/auth/login/")
def get_search_result(request, search_word):
    from news.models import News, NewsPortal
    return News.objects.filter(Q(news_title__contains=search_word) | Q(news_post_text__contains=search_word)).values()


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
    return User.objects.filter(is_staff=True).filter(Q(username__contains=search_word))


def get_company(request, search_word):
    from news.models import Companies
    return Companies.objects.filter(Q(name__contains=search_word))
