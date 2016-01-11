from django.contrib import auth
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.shortcuts import render_to_response, RequestContext
from django.db.models import Q


from news.models import NewsWatches, News, Companies
from search.models import UserRequests


#   @login_required(login_url="/auth/login/")
def render_search_page(request, template="search.html", news_search_template="news_search_template.html", extra_context=None, translate="english"):
    args = {
        "latest_news": get_latest_news_total(request)[:5],
        "news_search_template": news_search_template,
    }
    if request.is_ajax():
        template = news_search_template


    if "q" in request.GET and request.GET["q"]:
        search_word = request.GET["q"]
        args["users_count"] = get_search_among_users(request, search_word).count()
        args["companies_count"] = get_company(request, search_word).count()
        args["news_count"] =get_search_result(request, search_word).count()
        if search_word is "":
            args["erorr_empty_field"] = True
        #elif len(get_search_result_text(request, search_word)) < 1 and len(get_search_result_text(request, search_word)) < 1\
        #        and len(get_search_among_users(request, search_word)) < 1 and len(get_company(request, search_word)) < 1:
         #   args["empty_result"] = True
         #   args["popular_news"] = get_popular_news(request)
        else:
            args["results"] = get_search_result(request, search_word)
            args["matches_amount"] = get_matches_amount(request, search_word)
            args["users_matches"] = get_search_among_users(request, search_word)
            args["companies_matches"] = get_company(request, search_word).values()
        args["search_word"] = search_word
        if auth.get_user(request).username:
            args["username"] = User.objects.get(username=auth.get_user(request).username)
            args["search_private"] = True
            UserRequests.objects.create(
                user_id=User.objects.get(username=auth.get_user(request).username).id,
                request=search_word
            )
        else:
            UserRequests.objects.create(
                user_id=User.objects.get(username="eprivalov").id,
                request=search_word
            )
    args.update(csrf(request))
    return render_to_response(template, args, context_instance=RequestContext(request))


def get_latest_news_total(request):
    latest_10_news = News.objects.all().order_by("-news_post_date")
    return latest_10_news


#   @login_required(login_url="/auth/login/")
def get_search_result(request, search_word):
    companies_list = Companies.objects.filter(Q(name__contains=search_word[1:]) |
                                              Q(name__contains=search_word[1:])).values("id")
    return News.objects.filter(Q(news_title__contains=search_word) |
                               Q(news_company_owner_id__in=companies_list) |
                               Q(news_post_text_russian__contains=search_word) |
                               Q(news_post_text_english__contains=search_word) |
                               Q(news_post_text_chinese__contains=search_word)).values()


#   @login_required(login_url="/auth/login/")
def get_search_result_text(request, search_word):
    return News.objects.filter(Q(news_post_text_english__contains=search_word) |
                               Q(news_post_text_russian__contains=search_word) |
                               Q(news_post_text_chinese__contains=search_word)).order_by("-news_post_date").values()


#   @login_required(login_url="/auth/login/")
def get_matches_amount(request, search_word):
    companies_list = Companies.objects.filter(Q(name__contains=search_word.capitalize()) |
                                              Q(name__contains=search_word)).values("id")
    news = News.objects.filter(Q(news_title__contains=search_word) |
                               Q(news_company_owner_id__in=companies_list) |
                               Q(news_post_text_russian__contains=search_word) |
                               Q(news_post_text_english__contains=search_word) |
                               Q(news_post_text_chinese__contains=search_word)).count()
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
    return Companies.objects.filter(Q(name__contains=search_word) | Q(verbose_name__contains=search_word) |
                                    Q(name__contains=search_word.capitalize()))
