from django.contrib import auth
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.shortcuts import render_to_response, RequestContext
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
import json

from news.models import NewsWatches, News, Companies
from search.models import UserRequests


#   @login_required(login_url="/auth/login/")
def render_search_page(request, template="search.html", news_search_template="news_search_template.html", extra_context=None):
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
        # args["news_count"] = len(get_search_result(request, search_word))
        if search_word is "":
            args["erorr_empty_field"] = True
        else:
            # translation = {
            #     "id": "id",
            #     "news_title_english": "news_title_english",
            #     "news_title_russian": "news_title_russian",
            #     "news_title_chinese": "news_title_chinese",
            #     "teaser_english": "teaser_english",
            #     "teaser_russian": "teaser_russian",
            #     "teaser_chinese": "teaser_chinese",
            #     "news_post_date": "news_post_date",
            #     "slug": "slug"
            # }
            #
            # query = "SELECT id, news_title_english, news_title_russian, news_title_chinese, teaser_english, teaser_chinese, teaser_russian, slug, news_post_date FROM news " \
            #         " WHERE news_title_english LIKE %{phrase}%" \
            #         " or news_title_russian LIKE %{phrase}%" \
            #         " or news_title_chinese LIKE %{phrase}%" \
            #         " or teaser_english LIKE %{phrase}%" \
            #         " or teaser_russian LIKE %{phrase}%" \
            #         " or teaser_chinese LIKE %{phrase}%".format(phrase=search_word)
            #
            # data = News.objects.raw(raw_query=query, translations=translation)

            args["results"] = get_search_result(request, search_word=search_word)
            args["news_count"] = get_search_result(request, search_word=search_word).count()
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
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response(template, args, context_instance=RequestContext(request))


def get_news_for_footer(request):
    translation = {
        "id": "id",
        "news_title_english": "news_title_english",
        "news_title_russian": "news_title_russian",
        "news_title_chinese": "news_title_chinese",
        "slug": "slug"
    }
    return News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, slug FROM news ORDER BY news_post_date DESC LIMIT 3", translations=translation)

def get_latest_news_total(request):
    translation = {
        "id": "id",
        "news_title_english": "news_title_english",
        "news_title_russian": "news_title_russian",
        "news_title_chinese": "news_title_chinese",
        "slug": "slug"
    }
    latest_10_news = News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, slug, news_post_date FROM news ORDER BY news_post_date DESC LIMIT 5", translations=translation)
    return latest_10_news


#   @login_required(login_url="/auth/login/")
def get_search_result(request, search_word):
    companies_list = Companies.objects.filter(Q(name__contains=search_word[1:]) |
                                              Q(name__contains=search_word[1:])).values("id")
    translation = {
        "id": "id",
        "news_title_english": "news_title_english",
        "news_title_russian": "news_title_russian",
        "news_title_chinese": "news_title_chinese",
        "teaser_english": "teaser_english",
        "teaser_russian": "teaser_russian",
        "teaser_chinese": "teaser_chinese",
        "news_post_date": "news_post_date",
        "slug": "slug"
    }

    # data = News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese,"
    #                         " teaser_english, teaser_chinese, teaser_russian, slug, news_post_date FROM news"
    #                         " WHERE %s in news_title_english" % search_word, translations=translation)

    # return data

    return News.objects.filter(Q(news_title_english__contains=search_word) |
                               Q(news_title_chinese__contains=search_word) |
                               Q(news_title_russian__contains=search_word) |
                               Q(teaser_english__contains=search_word) |
                               Q(teaser_russian__contains=search_word) |
                               Q(teaser_chinese__contains=search_word) |
                               Q(news_company_owner_id__in=companies_list) |
                               Q(news_post_text_russian__contains=search_word) |
                               Q(news_post_text_english__contains=search_word) |
                               Q(news_post_text_chinese__contains=search_word))


def get_search_preview_result(request, search_word):
    companies_list = Companies.objects.filter(Q(name__contains=search_word[1:]) |
                                              Q(name__contains=search_word[1:])).values("id")
    result = News.objects.all().filter(Q(news_title_english__contains=search_word) |
                                       Q(news_title_russian__contains=search_word) |
                                       Q(news_title_chinese__contains=search_word) |
                                       Q(teaser_english__contains=search_word) |
                                       Q(teaser_russian__contains=search_word) |
                                       Q(teaser_chinese__contains=search_word) |
                               Q(news_company_owner_id__in=companies_list) |
                               Q(news_post_text_russian__contains=search_word) |
                               Q(news_post_text_english__contains=search_word) |
                               Q(news_post_text_chinese__contains=search_word))[:10]
    data = {
        'data': [i.get_json_for_search() for i in result.all()]
    }
    return HttpResponse(json.dumps([i.get_json_for_search() for i in result.all()]), content_type='application/json')


#   @login_required(login_url="/auth/login/")
def get_search_result_text(request, search_word):
    return News.objects.filter(Q(news_post_text_english__contains=search_word) |
                               Q(news_post_text_russian__contains=search_word) |
                               Q(news_post_text_chinese__contains=search_word)).order_by("-news_post_date").values()


#   @login_required(login_url="/auth/login/")
def get_matches_amount(request, search_word):
    companies_list = Companies.objects.filter(Q(name__contains=search_word.capitalize()) |
                                              Q(name__contains=search_word)).values("id")
    news = News.objects.filter(Q(news_title_english__contains=search_word) |
                               Q(news_title_russian__contains=search_word) |
                               Q(news_title_chinese__contains=search_word) |
                               Q(teaser_english__contains=search_word) |
                               Q(teaser_russian__contains=search_word) |
                               Q(teaser_chinese__contains=search_word) |
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
    return User.objects.filter(is_staff=True).filter(Q(username__contains=str(search_word).capitalize()) |
                                                     Q(username__contains=str(search_word).upper()) |
                                                     Q(username__contains=str(search_word).lower()))

def get_company(request, search_word):
    return Companies.objects.filter(Q(name__contains=search_word) | Q(verbose_name__contains=search_word) |
                                    Q(name__contains=search_word.capitalize()))
