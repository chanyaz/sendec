# -*-coding: utf-8 -*-

from django.shortcuts import render_to_response, RequestContext
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import Q
from .models import News, NewsCategory, Companies, TopVideoContent, RssNews, RssPortals, NewsWatches, RssNewsCovers, TopNews, NewsPortal,UserRssNewsReading, RSSChannels
import datetime
import json
from userprofile.models import UserLikesNews, UserSettings, UserProfile, UserRssPortals
from django.core.mail import send_mail
from favourite.models import RssSaveNews

import urllib.request as r



def render_robots(requets):
    return render_to_response('robots.txt')
def render_cn_ver(request):
    args = {}
    args.update(csrf(request))
    return render_to_response("insydia.com.html", args)



# def global_redirect(request):
#     if request.COOKIES.get("translate-version"):
#         if "russian" in request.COOKIES.get("translate-version"):
#             return HttpResponseRedirect("/ru/")
#         elif "english" in request.COOKIES.get("translate-version"):
#             return HttpResponseRedirect("/en/")
#         elif "chinese" in request.COOKIES.get("translate-version"):
#             return HttpResponseRedirect("/cn/")
#     else:
#         return HttpResponseRedirect("/en/")
#
#
# def translate_russian(request):
#     return main_page_load(request, translate="russian")
#
#
# def translate_chinese(request):
#     return main_page_load(request, translate="chinese")

def get_region_code():
    url = "http://ip-api.com/json"
    t = r.urlopen(url)
    data = json.loads(t.read().decode(t.info().get_param('charset') or 'utf-8'))
    return data['countryCode']


def main_page_load(request, template="index_beta.html", page_template="page_template.html", extra_context=None):
    instance = render_news_by_sendec(request)
    name_map = {'id': 'id',
                'news_title_english': 'news_title_english',
                'news_title_russian': 'news_title_russian',
                'news_title_chinese': 'news_title_chinese',
                'news_post_date': 'news_post_date',
                'news_author': 'news_author_id',
                }
    args = {
        "current_year": datetime.datetime.now().year,
        "title": "Home Page | ",
        "news_block": True,
        "total_middle_news": instance[0:4],
        "total_bottom_news": instance[4:6],
        "interest": get_hottest_news(request, category_id=5),
        "test_ids": NewsWatches.objects.order_by("-watches").values("news_id")[:4].values(),
        "before_reviews": get_before_reviews(request, category_id=None),

        "pre_total": list(News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese news_post_date, news_author_id FROM news ORDER BY news_post_date DESC OFFSET 9 LIMIT 3;", translations=name_map)),

        "total_news": list(News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_author_id FROM news ORDER BY news_post_date DESC OFFSET 12;", translations=name_map)),#get_total_news),
        "page_template": page_template,
        "top_news": get_top_total_news(request),
        "left_bar": True,
    }

    # LANGUAGE SETTER
    if not request.COOKIES.get('lang'):
        region = get_region_code()
        if region == 'RU': args['lang'] = 'rus'
        elif region == "US": args['lang'] = 'eng'
        else: args['lang'] = 'ch'
    else:
        if 'rus' in request.COOKIES.get('lang'): args['lang'] = 'rus'
        elif 'eng' in request.COOKIES.get('lang'): args['lang'] = 'eng'
        elif 'ch' in request.COOKIES.get('lang'): args['lang'] = 'ch'

    if request.is_ajax():
        template = page_template
    args.update(csrf(request))
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = get_news_for_footer(request)[:3]
    response = render_to_response([template, "footer.html"], context=args, context_instance=RequestContext(request))
    # COOKIE SETTER
    if not request.COOKIES.get('lang'):
        region = get_region_code()
        if region == 'RU': response.set_cookie("lang", "rus")
        elif region == "US": response.set_cookie("lang", "eng")
        else: response.set_cookie("lang", "ch")
    else:
        pass
    return response


def get_latest_reviews(request):
    return News.objects.filter(news_category_id=6).order_by("-news_post_date").values()[0]
def get_before_reviews(request, category_id):
    translation = {
        "id": "id",
        "news_title_english": "news_title_english",
        "news_title_russian": "news_title_russian",
        "news_title_chinese": "news_title_chinese",
        "news_post_date": "news_post_date",
        "news_author": "news_author_id",
        "news_company_owner": "news_company_owner_id",
        "news_main_cover": "news_main_cover",
        "teaser_english": "teaser_english",
        "teaser_russian": "teaser_russian",
        "teaser_chinese": "teaser_chinese",
        "slug": "slug",
    }
    if category_id != None:
        return News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, teaser_english, teaser_russian, teaser_chinese, news_post_date, news_author_id, news_company_owner_id, news_main_cover,"
                                "slug FROM news WHERE news_category_id=%s ORDER BY news_post_date DESC OFFSET 6 LIMIT 3;" % category_id, translations=translation)
    else:
        return News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, teaser_english, teaser_russian, teaser_chinese, news_post_date, news_author_id, news_company_owner_id, news_main_cover,"
                                "slug FROM news ORDER BY news_post_date DESC OFFSET 6 LIMIT 3;", translations=translation)
def get_hottest_news(request, category_id):
    translation = {
        "id": "id",
        "news_title_english": "news_title_english",
        "news_title_russian": "news_title_russian",
        "news_title_chinese": "news_title_chinese",
        "news_post_date": "news_post_date",
        "news_author": "news_author_id",
        "news_company_owner_": "news_company_owner_id",
        "news_main_cover": "news_main_cover",
        "slug": "slug"
    }
    # watches = NewsWatches.objects.order_by("-watches").values("news_id").values("news_id")
    # watches_list = [int(watches[i]["news_id"]) for i in range(len(watches[:4]))]
    # if len(watches_list) >= 4:
    if category_id != None:
        return News.objects.raw("SELECT n.id, n.news_title_english, n.news_title_russian, n.news_title_chinese, n.news_post_date, n.news_author_id, n.news_company_owner_id, n.news_main_cover FROM news n INNER JOIN news_watches nw ON n.id=nw.news_id WHERE n.news_category_id=%s ORDER BY nw.watches DESC LIMIT 4" % category_id, translations=translation)
    else:
        return News.objects.raw("SELECT n.id, n.news_title_english, n.news_title_russian, n.news_title_chinese, n.news_post_date, n.news_author_id, n.news_company_owner_id, n.news_main_cover FROM news n INNER JOIN news_watches nw ON n.id=nw.news_id ORDER BY nw.watches DESC LIMIT 4", translations=translation)
    # else:
    #     return News.objects.all().order_by("-news_post_date").values()[:4]
def get_top_total_news(request):
    name_map = {'id': 'id',
                'top_news_title_english': 'top_news_title_english',
                'top_news_title_russian': 'top_news_title_russian',
                'top_news_title_chinese': 'top_news_title_chinese',
                'top_news_post_date': 'top_news_post_date',
                # 'news_category': 'news_category_id',
                'top_news_author': 'top_news_author_id',
                "slug": "slug",
                }
    # return TopNews.objects.all()[:4].defer("top_news_post_text_english").defer("top_news_post_text_russian").defer("top_news_post_text_chinese").values()
    return TopNews.objects.raw("SELECT id, top_news_title_english, top_news_title_russian, top_news_title_chinese, top_news_author_id, top_news_post_date, slug  FROM news_top ORDER BY id DESC limit 1;", translations=name_map)
def get_total_news():
    name_map = {'id': 'id',
                'news_title_english': 'news_title_english',
                'news_title_russian': 'news_title_english',
                'news_title_chinese': 'news_title_chinese',
                'news_post_date': 'news_post_date',
                # 'news_category': 'news_category_id',
                'news_author': 'news_author_id',
                # "slug": "slug",
                }
    #return News.objects.all().values()[9:]
    return News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, teaser_english, teaser_russian, teaser_chinese, news_post_date, news_author FROM "
                            "(SELECT ROW_NUMBER() OVER (PARTITION BY id ORDER BY news_post_date DESC) AS OrderedDate, * FROM news) as newsList"
                            "WHERE OrderedDate=5 ORDER BY news_post_date DESC;", translations=name_map)
def render_news_by_sendec(request, **kwargs):
    name_map = {'id': 'id',
                'news_title_english': 'news_title_english',
                'news_title_russian': 'news_title_russian',
                'news_title_chinese': 'news_title_chinese',
                'news_post_date': 'news_post_date',
                'teaser_english': 'teaser_english',
                'teaser_russian': 'teaser_russian',
                'teaser_chinese': 'teaser_chinese',
                'news_category': 'news_category_id',
                "slug": "slug",
                }
    # if len(kwargs) > 0:
    #     instance = News.objects.raw("SELECT id, news_title from news ORDER BY news_post_date news limit 9;", translations=name_map).filter(news_category_id=kwargs["category_id"]).exclude(id=kwargs["news_id"])
    #     return instance
    # else:
    if len(kwargs) > 0:
        category_id = kwargs['category_id']
        return News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, teaser_english, teaser_russian, teaser_chinese from news WHERE news_category_id in (%s);" % category_id, translations=name_map)
    else:
        return News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, teaser_english, teaser_russian, teaser_chinese, news_post_date from news ORDER BY news_post_date DESC;", translations=name_map)
def get_company_news(request, news_id, company_id):
    current_company_news = News.objects.filter(news_company_owner=
                                               company_id).exclude(id=news_id).order_by("-news_post_date")
    return current_company_news
def get_latest_news_total(request):
    latest_10_news = News.objects.all().order_by("-news_post_date")
    return latest_10_news
def render_current_top_news(request, news_id, slug):
    # current_top_news = TopNews.objects.get(slug=slug)
    translation = {
        "id": "id",
        "top_news_title_english": "top_news_title_english",
        "top_news_title_russian": "top_news_title_russian",
        "top_news_title_chinese": "top_news_title_chinese",
        "top_news_category": "top_news_category_id",
        "top_news_post_date": "top_news_post_date",
        "top_news_post_text_english": "top_news_post_text_english",
        "top_news_portal_name": "top_news_portal_name_id",
        "top_news_company_owner": "top_news_company_owner_id",
        "top_news_author": "top_news_author_id",
        "top_news_main_cover": "top_news_main_cover",
        "top_news_tags": "top_news_tags",
        "slug": "slug",
    }
    current_top_news = TopNews.objects.raw("SELECT * FROM news_top where slug='%s';" % slug, translations=translation)
    args = {
        "other_materials": current_top_news_other_materials(request, news_id),
        "other_materials_bottom": current_top_news_other_materials_bottom(request, news_id),
        "left_bar": True
    }
    args["current_top_news_values"] = current_top_news[0]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
        args["title"] = "%s | " % current_top_news[0].top_news_title_english
        args["current_top_news_title"] = current_top_news[0].top_news_title_english
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
        args["title"] = "%s | " % current_top_news[0].top_news_title_russian
        args["current_top_news_title"] = current_top_news[0].top_news_title_russian
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
        args["title"] = "%s | " % current_top_news[0].top_news_title_chinese
        args["current_top_news_title"] = current_top_news[0].top_news_title_chinese

    args.update(check_english(current_top_news[0], flag=1))

    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response("top_news.html", args, context_instance=RequestContext(request))


def render_current_news(request, year, month, day, news_id, slug):
    translation = {
        "id": "id",
        "news_title_english": "news_title_english",
        "news_title_russian": "news_title_russian",
        "news_title_chinese": "news_title_chinese",
        "news_category": "news_category_id",
        "news_post_date": "news_post_date",
        "news_post_text_english": "news_post_text_english",
        "news_portal_name": "news_portal_name_id",
        "news_company_owner": "news_company_owner_id",
        "news_author": "news_author_id",
        "news_main_cover": "news_main_cover",
        "news_tags": "news_tags",
        "slug": "slug",
    }
    current_news = News.objects.raw("SELECT * FROM news where slug='%s';" % slug, translations=translation)
    args = {
        "other_materials": current_news_other_materials(request, news_id, current_news[0].news_category_id),
        "other_materials_bottom": current_news_other_materials_bottom(request, news_id, current_news[0].news_category_id),
        "current_day": datetime.datetime.now().day,
        "left_bar": True,
    }
    if not request.COOKIES.get('lang'):
        region = get_region_code()
        if region == 'RU': args['lang'] = 'rus'
        elif region == "US": args['lang'] = 'eng'
        else: args['lang'] = 'ch'
    else:
        if 'rus' in request.COOKIES.get('lang'):
            args['lang'] = 'rus'
            args["title"] = "%s | " % current_news[0].news_title_russian
            args["current_news_title"] = current_news[0].news_title_russian
        elif 'eng' in request.COOKIES.get('lang'):
            args['lang'] = 'eng'
            args["title"] = "%s | " % current_news[0].news_title_english
            args["current_news_title"] = current_news[0].news_title_english
        elif 'ch' in request.COOKIES.get('lang'):
            args['lang'] = 'ch'
            args["title"] = "%s | " % current_news[0].news_title_chinese
            args["current_news_title"] = current_news[0].news_title_chinese


    category_id = current_news[0].news_category
    args["current_news_values"] = current_news[0]
    # args["company_name"] = str(Companies.objects.get(id=current_news[0].news_company_owner)).capitalize(),
    args.update(check_english(current_news[0], flag=0))

    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    addition_news_watches(request, news_id)
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    response = render_to_response("current_news_beta.html", args, context_instance=RequestContext(request))
    if not request.COOKIES.get('lang'):
        region = get_region_code()
        if region == 'RU': response.set_cookie("lang", "rus")
        elif region == "US": response.set_cookie("lang", "eng")
        else: response.set_cookie("lang", "ch")
    else:
        pass
    return response


def current_news_other_materials(request, news_id, category_id):
    translation = {
        "id": "id",
        "news_title_english": "news_title_english",
        "news_title_russian": "news_title_russian",
        "news_title_chinese": "news_title_chinese",
        "news_post_date": "news_post_date",
        "news_main_cover": "news_main_cover"
    }
    return News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_main_cover from news WHERE news_category_id=%s and id != %s ORDER BY news_post_date DESC limit 4;" % (category_id, news_id),
                            translations=translation)
def current_news_other_materials_bottom(request, news_id, category_id):
    translation = {
        "id": "id",
        "news_title": "news_title",
        "news_post_date": "news_post_date",
        "news_main_cover": "news_main_cover"
    }
    return News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_main_cover from news WHERE news_category_id=%s ORDER BY news_post_date DESC OFFSET 4 limit 3;" % category_id,
                            translations=translation)

def current_top_news_other_materials(request, news_id):
    translation = {
        "id": "id",
        "news_title_english": "news_title_english",
        "news_title_russian": "news_title_russian",
        "news_title_chinese": "news_title_chinese",
        "news_post_date": "news_post_date",
        "news_main_cover": "news_main_cover"
    }
    return News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_main_cover from news ORDER BY news_post_date DESC limit 4;",
                            translations=translation)
def current_top_news_other_materials_bottom(request, news_id):
    translation = {
        "id": "id",
        "news_title_english": "news_title_english",
        "news_title_russian": "news_title_russian",
        "news_title_chinese": "news_title_chinese",
        "news_post_date": "news_post_date",
        "news_main_cover": "news_main_cover"
    }
    return News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_main_cover from news ORDER BY news_post_date DESC OFFSET 4 limit 3;",
                            translations=translation)

def check_english(news, flag):
    args = {}
    if flag == 0:
        if news.news_post_text_english != "":
            args["eng"] = True
        if news.news_post_text_russian != "":
            args["rus"] = True
        if news.news_post_text_chinese != "":
            args["ch"] = True
        return args
    elif flag == 1:
        if news.top_news_post_text_english != "":
            args["eng"] = True
        if news.top_news_post_text_russian != "":
            args["rus"] = True
        if news.top_news_post_text_chinese != "":
            args["ch"] = True
        return args
    else:
        pass


@login_required(login_url="/auth/login/")
def render_user_news(request, template="user_news_beta.html", rss_template="rss_template.html", extra_context=None):
    user = User.objects.get(username=auth.get_user(request).username)
    if get_user_rss_portals(request, user_id=user.id).count() == 0:
        """If RSS portals list is empty for current user
        """
        return HttpResponseRedirect('/news/browser/')
    else:
        user_rss_list = UserRssPortals.objects.filter(user_id=user.id).filter(check=True).values("id")
        args = {
            "title": "My news | ", "user_rss": get_user_rss_news(request, user_id=user.id).order_by("position"),
            "user_rss_count": get_user_rss_news(request, user_id=user.id).order_by("position").count(),
            "popular_rss": get_most_popular_rss_portals(request)[:9],
            "popular_rss_right": get_most_popular_rss_portals(request)[:3],
            "rss_template": rss_template,
            "un_us_p": get_user_unselceted_portals(request, user_id=user.id),
            "un_us_p_count": get_user_unselceted_portals(request, user_id=user.id).count(),
            "if_zero": "<p>Wow, you are reading all of our portals. Would you like to <a href='/about/contacts/'>tell</a> us something?</p><p>Or you just can "
                       "write which portal you want to see here and we will try to add it to our database with pleasure.</p>"
                       "<p>You are our <b>HERO</b>, man!</p>",
            "new_user_news": get_rss_filterd(request, user.id).distinct(),
            "user_rss_portals": get_user_rss_portals(request, user_id=user.id),
            "left_bar": False,
            "here_private": True,
            "rss_tech": RssPortals.objects.filter(category=1)[:4],
            "rss_ent": RssPortals.objects.filter(category=2)[:4],
            "rss_auto": RssPortals.objects.filter(category=3)[:4],
            "rss_space": RssPortals.objects.filter(category=4)[:4],
            "rss_bio": RssPortals.objects.filter(category=5)[:4]
        }

        args.update(csrf(request))
        if auth.get_user(request).username:
            args["username"] = User.objects.get(username=auth.get_user(request).username)
            args["search_private"] = True
        args["rss_news"] = set_rss_for_user_test(request)
        args["rss_news_count"] = set_rss_for_user_test(request).count()
        if request.is_ajax():
            template = rss_template
        if get_user_rss_news(request, user_id=user.id).count() == 0:
            args["zero"] = True
        else:
            args["zero"] = False
        args["footer_news"] = get_news_for_footer(request)[:3]
        args["body_color"] = True
        if "eng" in request.COOKIES.get('lang'):
            args['lang'] = 'eng'
        elif "rus" in request.COOKIES.get('lang'):
            args['lang'] = 'rus'
        elif "ch" in request.COOKIES.get('lang'):
            args['lang'] = 'ch'
        return render_to_response(template, context=args, context_instance=RequestContext(request))


def get_rss_filterd(request, user_id):
    user_portals_ids = UserRssPortals.objects.filter(user_id=user_id).filter(check=True).values("portal_id")
    list_ids = [user_portals_ids[i]["portal_id"] for i in range(len(user_portals_ids))]
    return RssNews.objects.filter(portal_name_id__in=list_ids, portal_name_id__userrssportals__user_id=user_id).order_by("portal_name_id__userrssportals__position").order_by("-date_posted").defer("author").defer("content_value").values()


def get_user_unselceted_portals(request, user_id):
    return UserRssPortals.objects.filter(user_id=user_id).filter(check=False)


def get_user_rss_portals(request, user_id):
    return UserRssPortals.objects.filter(user_id=user_id).filter(check=True).values()


def get_most_popular_rss_portals(request):
    return RssPortals.objects.all().order_by("follows").values()


def get_user_chosen_portals(request):
    return UserSettings.objects.get(user_id=
                                    User.objects.get(username=
                                                     auth.get_user(request).username).id).portals_to_show.split(",")


def get_rss_news_pagination(request, current_page, next_page):
    data_rss_news = [current_new.get_json_rss() for current_new in RssNews.objects.all()[current_page:next_page]]
    response_data = {
        "rss": data_rss_news,
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def get_current_rss_news(request, news_id):
    news_instance = RssNews.objects.get(id=int(news_id))
    instance = RssNews.objects.get(id=int(news_id)).get_json_rss()


    b = ""
    if request.COOKIES.get("lang") == "eng": b = "Close"
    elif request.COOKIES.get("lang") == "rus": b = "Закрыть"
    elif request.COOKIES.get("lang") == "cn": b = "cn"


    string = """<div class="cur-pw-top" data-rss-id="{data_id}">
    <div class="cur-pw-background"></div>
    <div class="cur-pw-btn-bck"></div>

    <div class="cur-pw-description col-md-12" style="position: absolute; top: 3em;">
        <h1 class="rss-title-preview-new text-center">{title}</h1>
        <div class="cur-pw-td text-center">By <span class="rss-author-new">{author}</span></div>
    </div>
        <div class="col-md-12 col-xs-12" style="position: absolute; bottom: 0;">
            <ul id="rss-share-list" class="">
                <li class="rss-share-item">
                    <a data-target-link="{link}" class="rss-share-facebook" onclick="window.open(
                        'http://facebook.com/sharer/sharer.php?u='+$(this).attr('data-target-link'),
                         'JSSite', 'width=420,height=230,resizable=yes,scrollbars=yes,status=yes')">
                        <span class="fa fa-facebook social-rss" style="font-size: 1.5em; "></span>
                    </a>
                </li>
                <li class="rss-share-item">
                    <a data-target-link="{link}" class="rss-share-vk" onclick="window.open('https://vk.com='+$(this).attr('data-target-link'),
                         'JSSite', 'width=420,height=230,resizable=yes,scrollbars=yes,status=yes')">
                        <span class="fa fa-vk social-rss" style="font-size: 1.5em;"></span>
                    </a>
                </li>
                <li class="rss-share-item">
                    <a data-target-link="{link}" class="rss-share-twitter"
                    onclick="window.open('https://twitter.com/intent/tweet?original_referer='+'https://insydia.com/'+'&ref_src=twsrc%5Etfw&%20%7C%20%C2%A0Insydia&tw_p=tweetbutton&url='+$(this).attr('data-target-link')+'&via=InsydiaNews',
                         'JSSite', 'width=420,height=230,resizable=yes,scrollbars=yes,status=yes')">
                        <span class="fa fa-twitter social-rss" style="font-size: 1.5em;"></span>
                    </a>
                </li>
                <li class="rss-share-item">
                    <a data-target-link="{link}" class="rss-share-linkedin" onclick="window.open('https://www.linkedin.com/shareArticle?mini=true&url='+$(this).attr('data-target-link')+'&title='+'TITLE'+'&summary='+'summary',
                         'JSSite', 'width=420,height=230,resizable=yes,scrollbars=yes,status=yes');">
                        <span class="fa fa-linkedin social-rss" style="font-size: 1.5em;"></span>
                    </a>
                </li>
            </ul>
        </div>

</div>

</div>

<div class="rss-preview-body"></div>
    """.format(title=news_instance.title,
               author=news_instance.author if news_instance.author else news_instance.portal_name,
               read=123,
               data_id=news_instance.id,
               likes=321,
               link=news_instance.link,
               body=news_instance.content_value if news_instance.content_value else news_instance.post_text)





    response_data = {
        "data": instance,
        "string": string,
    }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def get_current_rss_news_mobile(request, news_id):
    news_instance = RssNews.objects.get(id=int(news_id))
    instance = RssNews.objects.get(id=int(news_id)).get_json_rss()


    b = ""
    if request.COOKIES.get("lang") == "eng": b = "Close"
    elif request.COOKIES.get("lang") == "rus": b = "Закрыть"
    elif request.COOKIES.get("lang") == "cn": b = "cn"


    string = """<div class="cur-pw-top" data-rss-id="{data_id}">
    <div class="cur-pw-background"></div>
    <div class="cur-pw-btn-bck"></div>

    <div class="cur-pw-description col-md-12" style="position: absolute; top:0;">
        <h1 class="rss-title-preview-new text-center">{title}</h1>
        <div class="cur-pw-td text-center">By <span class="rss-author-new">{author}</span></div>
    </div>
        <div class="pull-left" style="position: absolute; bottom: 0; left:0;">
            <button class="btn btn-primary" onclick="RssPreviewArticleMobileHide();return false;" style="font-size:10px;">Close</button>
        </div>
        <div class="col-md-12 col-xs-9 col-xs-offset-2" style="position: absolute; bottom: 0;">
            <ul id="rss-share-list" class="">
                <li class="rss-share-item">
                    <a data-target-link="{link}" class="rss-share-facebook" onclick="window.open(
                        'http://facebook.com/sharer/sharer.php?u='+$(this).attr('data-target-link'),
                         'JSSite', 'width=420,height=230,resizable=yes,scrollbars=yes,status=yes')">
                        <span class="fa fa-facebook social-rss" style="font-size: 1.5em; "></span>
                    </a>
                </li>
                <li class="rss-share-item">
                    <a data-target-link="{link}" class="rss-share-vk" onclick="window.open('https://vk.com='+$(this).attr('data-target-link'),
                         'JSSite', 'width=420,height=230,resizable=yes,scrollbars=yes,status=yes')">
                        <span class="fa fa-vk social-rss" style="font-size: 1.5em;"></span>
                    </a>
                </li>
                <li class="rss-share-item">
                    <a data-target-link="{link}" class="rss-share-twitter"
                    onclick="window.open('https://twitter.com/intent/tweet?original_referer='+'https://insydia.com/'+'&ref_src=twsrc%5Etfw&%20%7C%20%C2%A0Insydia&tw_p=tweetbutton&url='+$(this).attr('data-target-link')+'&via=InsydiaNews',
                         'JSSite', 'width=420,height=230,resizable=yes,scrollbars=yes,status=yes')">
                        <span class="fa fa-twitter social-rss" style="font-size: 1.5em;"></span>
                    </a>
                </li>
                <li class="rss-share-item">
                    <a data-target-link="{link}" class="rss-share-linkedin" onclick="window.open('https://www.linkedin.com/shareArticle?mini=true&url='+$(this).attr('data-target-link')+'&title='+'TITLE'+'&summary='+'summary',
                         'JSSite', 'width=420,height=230,resizable=yes,scrollbars=yes,status=yes');">
                        <span class="fa fa-linkedin social-rss" style="font-size: 1.5em;"></span>
                    </a>
                </li>
            </ul>
        </div>

</div>

</div>

<div class="rss-preview-body"></div>
    """.format(title=news_instance.title,
               author=news_instance.author if news_instance.author else news_instance.portal_name,
               read=123,
               data_id=news_instance.id,
               likes=321,
               link=news_instance.link,
               body=news_instance.content_value if news_instance.content_value else news_instance.post_text)
    response_data = {
        "data": instance,
        "string": string,
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")



def get_rss_news(request):
    return RssNews.objects.all().values()


def render_top_news_page(request):
    args = {
        "top_news": get_top_news(request),
        "left_bar": True,
    }
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response("top_news.html", args)


def get_user_news_by_portals(request):
    inst = UserSettings.objects.get(user_id=
                                    User.objects.get(username=
                                                     auth.get_user(request).username).id)
    len_inst = inst.portals_to_show.count()
    split_inst=inst.split(",")
    total_news_2 = list(News.objects.filter(Q(news_portal_name_id=split_inst[cur_id])).order_by("-news_post_date") for cur_id
                        in range(len(split_inst)-1))
    return total_news_2


def test(request):
    from itertools import chain
    from operator import attrgetter

    inst_portals = UserSettings.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id).portals_to_show.split(",")
    inst_categories = UserSettings.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id).categories_to_show.split(",")
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


def check_like(request, news_id):
    if auth.get_user(request).is_authenticated():
        if UserLikesNews.objects.filter(user_id=User.objects.get(username=auth.get_user(request).username).id).filter(news_id=news_id).filter(like=True).exists():
            return True
        else:
            return False
    else:
        pass


def check_dislike(request, news_id):
    if auth.get_user(request).is_authenticated():
        if UserLikesNews.objects.filter(user_id=User.objects.get(username=auth.get_user(request).username).id).filter(news_id=news_id).filter(dislike=True).exists():
            return True
        else:
            return False
    else:
        pass


def update_latest_news(request):
    latest_new = News.objects.filter(news_latest_shown=False).order_by("-news_post_date")[0]
    string = """<span class='time' style='color: blue;'>%s</span>
<span class='title' onclick="location.href='/news/%s/%s/';">%s</span><br>""" \
             % (latest_new.news_post_date.time().strftime("%H:%M"), latest_new.news_category_id, latest_new.id,
                latest_new.news_title)

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
    instance = News.objects.get(id=int(news_id))
    instance.news_latest_shown = True
    instance.save()
    return HttpResponse()


# @login_required(login_url="/auth/login/")
def addition_news_watches(request, news_id):
    instance = NewsWatches.objects.filter(news_id=news_id)
    if instance.exists():
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
    top_list_id = NewsWatches.objects.all()[:10].values()
    top_news = [News.objects.get(id=int(cur_news_id["news_id"])) for cur_news_id in top_list_id]
    return top_news


def render_current_category(request, category_name):
    args = {
        "title": "Politics | ",
        "latest_news": get_latest_news_total(request),
        "category_title": category_name.capitalize(),
        "left_bar": True,
    }
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response("current_category.html", args)

#   ###########################################################################
#   ############################# CATEGORIES ##################################
#   ###########################################################################


def render_technology_news(request, template="technology.html", tech_template="tech_template.html", extra_context=None):
    instance = render_news_by_sendec(request, category_id=1)
    name_map = {'id': 'id',
                "news_title_english": "news_title_english",
                "news_title_russian": "news_title_russian",
                "news_title_chinese": "news_title_chinese",
                'news_post_date': 'news_post_date',
                'news_author': 'news_author_id',
                }
    args = {
        "current_year": datetime.datetime.now().year,
        "title": "Technology News | ",
        "total_middle_news": instance[0:4],
        "total_bottom_news": instance[4:6],
        "interest": get_hottest_news(request, category_id=1),
        "test_ids": NewsWatches.objects.order_by("-watches").values("news_id")[:4].values(),
        "before_reviews": get_before_reviews(request, category_id=1),

        "pre_total": list(News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_author_id FROM news WHERE news_category_id=1 ORDER BY news_post_date DESC OFFSET 9 LIMIT 3;", translations=name_map)),

        "total_news": list(News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_author_id FROM news WHERE news_category_id=1 ORDER BY news_post_date DESC OFFSET 12;", translations=name_map)),#get_total_news),
        "page_template": tech_template,
        "top_news": get_top_total_news(request),
        "left_bar": True,
    }
    if request.is_ajax():
        template = tech_template
    args.update(csrf(request))
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    response = render_to_response([template, "footer.html"], context=args, context_instance=RequestContext(request))
    return response


def get_technology_news(request):
    return News.objects.all().filter(news_category_id=NewsCategory.objects.get(category_name="Technology").id)
#   #########3#################### END TECHNOLOGY #######################################


def get_category_news_offset(request, *args, **kwargs):
    return News.objects.filter(news_category_id=NewsCategory.objects.get(category_name=kwargs["category_name"])).order_by("-news_post_date").defer("news_post_text_chinese").defer("news_post_text_english").defer("news_post_text_russian").values()


def get_top_category_news(request, *args, **kwargs):
    """
    GET TOP NEWS OF CURRENT CATEGORY
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    return News.objects.filter(news_category_id=NewsCategory.objects.get(category_name=kwargs["category_name"])).order_by("-news_post_date").defer("news_post_text_chinese").defer("news_post_text_english").defer("news_post_text_russian").values()[0]


def render_auto_news(request, template="auto.html", auto_template="auto_template.html", extra_context=None):
    instance = render_news_by_sendec(request, category_id=3)
    name_map = {'id': 'id',
                'news_title': 'news_title',
                'news_post_date': 'news_post_date',
                'news_author': 'news_author_id',
                }
    args = {
        "current_year": datetime.datetime.now().year,
        "title": "Auto News | ",
        "total_middle_news": instance[0:4],
        "total_bottom_news": instance[4:6],
        "interest": get_hottest_news(request, category_id=3),
        "test_ids": NewsWatches.objects.order_by("-watches").values("news_id")[:4].values(),
        "before_reviews": get_before_reviews(request, category_id=3),

        "pre_total": list(News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_author_id FROM news WHERE news_category_id=3 ORDER BY news_post_date DESC OFFSET 9 LIMIT 3;", translations=name_map)),

        "total_news": list(News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_author_id FROM news WHERE news_category_id=3 ORDER BY news_post_date DESC OFFSET 12;", translations=name_map)),#get_total_news),
        "page_template": auto_template,
        "top_news": get_top_total_news(request),
        "left_bar": True,
    }
    if request.is_ajax():
        template = auto_template
    args.update(csrf(request))
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    response = render_to_response([template, "footer.html"], context=args, context_instance=RequestContext(request))
    return response


def get_auto_news(request):
    return News.objects.all().filter(news_category_id=NewsCategory.objects.get(category_name="Auto").id)
#   ################################## END AUTO #########################################


def render_bio_news(request, template="bio.html", bio_template="bio_template.html", extra_context=None):
    instance = render_news_by_sendec(request, category_id=5)
    name_map = {'id': 'id',
                'news_title': 'news_title',
                'news_post_date': 'news_post_date',
                'news_author': 'news_author_id',
                }
    args = {
        "current_year": datetime.datetime.now().year,
        "title": "Bio-tech news | ",
        "total_middle_news": instance[0:4],
        "total_bottom_news": instance[4:6],
        "interest": get_hottest_news(request, category_id=5),
        "test_ids": NewsWatches.objects.order_by("-watches").values("news_id")[:4].values(),
        "before_reviews": get_before_reviews(request, category_id=5),

        "pre_total": list(News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_author_id FROM news WHERE news_category_id=5 ORDER BY news_post_date DESC OFFSET 9 LIMIT 3;", translations=name_map)),

        "total_news": list(News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_author_id FROM news WHERE news_category_id=5 ORDER BY news_post_date DESC OFFSET 12;", translations=name_map)),#get_total_news),
        "page_template": bio_template,
        "top_news": get_top_total_news(request),
        "left_bar": True,
    }
    if request.is_ajax():
        template = bio_template
    args.update(csrf(request))
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    response = render_to_response([template, "footer.html"], context=args, context_instance=RequestContext(request))
    return response


def get_bit_news(request):
    return News.objects.all().filter(news_category_id=NewsCategory.objects.get(category_name="BIO").id)
#   ################################## END BIO #########################################


def render_companies_news(request, template="companies.html", companies_endless="companies_endless.html", extra_context=None):
    args = {
        "title": "Companies | ",
        "companies": get_companies(request),
        "category_title": "COMPANIES",
        # "companies_endless": companies_endless,

        "left_bar": True,
        "here_companies": True,
    }
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args.update(csrf(request))
    # if request.is_ajax():
    #     template = companies_endless
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response(template, args, context_instance=RequestContext(request))


def get_companies(request):
    return Companies.objects.all().order_by("id").defer("description").defer("site").defer("category")


def render_current_company(request, company_name, template="current_company.html", company_news="current_company_news.html", extra_context=None):
    from search import views as sv
    company = Companies.objects.get(verbose_name=company_name)
    args = {
        "title": company.name+" | ",
        "company": company,
        "company_news": company_news,
        "news": get_companies_news(request, company.id),
        "latest_news": sv.get_latest_news_total(request)[:5],
        "left_bar": True,
    }
    args.update(csrf(request))

    if request.is_ajax():
        template = company_news

    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response(template, args, context_instance=RequestContext(request))


def get_companies_news(request, company_id):
    return News.objects.filter(news_company_owner_id=company_id).order_by("-news_post_date").values()


#   #############################END COMPANIES###################################


def render_entertainment_news(request, template="entertainment.html", ent_template="ent_template.html", extra_context=None):
    instance = render_news_by_sendec(request, category_id=2)
    name_map = {'id': 'id',
                'news_title': 'news_title',
                'news_post_date': 'news_post_date',
                'news_author': 'news_author_id',
                }
    args = {
        "current_year": datetime.datetime.now().year,
        "title": "Entertainment News | ",
        "total_middle_news": instance[0:4],
        "total_bottom_news": instance[4:6],
        "interest": get_hottest_news(request, category_id=2),
        "test_ids": NewsWatches.objects.order_by("-watches").values("news_id")[:4].values(),
        "before_reviews": get_before_reviews(request, category_id=2),

        "pre_total": list(News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_author_id FROM news WHERE news_category_id=2 ORDER BY news_post_date DESC OFFSET 9 LIMIT 3;", translations=name_map)),

        "total_news": list(News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_author_id FROM news WHERE news_category_id=2 ORDER BY news_post_date DESC OFFSET 12;", translations=name_map)),#get_total_news),
        "page_template": ent_template,
        "top_news": get_top_total_news(request),
        "left_bar": True,
    }
    if request.is_ajax():
        template = ent_template
    args.update(csrf(request))
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    response = render_to_response([template, "footer.html"], context=args, context_instance=RequestContext(request))
    return response


def get_entertainment_news(request):
    return News.objects.all().filter(news_category_id=NewsCategory.objects.get(category_name="Entertainment").id)

#   ################## END ENTERTAINMENT ######################################3333


def render_latest_news(request):
    args = {
        "title": "Latest | ",
        "top_latest_news": get_latest_news_total(request)[0],
        "latest_news": get_latest_news_total(request)[1:10],
        "category_title": "LATEST",

        "left_bar": True,
    }
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response("latest.html", args)


def render_reviews_news(request):
    args = {
        "title": "Reviews | ",
        "latest_news": get_latest_news_total(request),
        "category_title": "REVIEWS",

        "left_bar": True,
        "here_review": True,
    }
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response("reviews.html", args)


def render_space_news(request, template="space.html", space_template="space_template.html", extra_context=None):
    instance = render_news_by_sendec(request, category_id=4)
    name_map = {'id': 'id',
                'news_title': 'news_title',
                'news_post_date': 'news_post_date',
                'news_author': 'news_author_id',
                }
    args = {
        "current_year": datetime.datetime.now().year,
        "title": "Space News | ",
        "total_middle_news": instance[0:4],
        "total_bottom_news": instance[4:6],
        "interest": get_hottest_news(request, category_id=4),
        "test_ids": NewsWatches.objects.order_by("-watches").values("news_id")[:4].values(),
        "before_reviews": get_before_reviews(request, category_id=4),
        "pre_total": list(News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_author_id FROM news WHERE news_category_id=4 ORDER BY news_post_date DESC OFFSET 9 LIMIT 3;", translations=name_map)),
        "total_news": list(News.objects.raw("SELECT id, news_title_english, news_title_russian, news_title_chinese, news_post_date, news_author_id FROM news WHERE news_category_id=4 ORDER BY news_post_date DESC OFFSET 12;", translations=name_map)),#get_total_news),
        "page_template": space_template,
        "top_news": get_top_total_news(request),
        "left_bar": True,
    }
    if request.is_ajax():
        template = space_template
    args.update(csrf(request))
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    response = render_to_response([template, "footer.html"], context=args, context_instance=RequestContext(request))
    return response


def get_space_news(request):
    return News.objects.all().filter(news_category_id=NewsCategory.objects.get(category_name="Space").id)


#   ################################### END SPACE ##############################3


def get_user_rss_news(request, user_id):
    return UserRssPortals.objects.filter(user_id=user_id).filter(check=True).values()


def get_updated_user_rss(request):
    user = User.objects.get(username=auth.get_user(request).username)
    portals = UserRssPortals.objects.filter(user_id=user.id).filter(check=True)
    data = [portal.get_json_portal() for portal in portals.all()]
    response_data = {
        "portals": data,
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def get_updated_rss(request):
    user = User.objects.get(username=auth.get_user(request).username)
    portals_user_list = get_user_rss_news(request, user_id=user.id)
    total_news = RssNews.objects.filter(portal_name_id__in=(portals_user_list[i]["portal_id"] for i
                                                            in range(len(portals_user_list))))
    news = [news.get_json_rss() for news in total_news]
    response_data = {
        "updated_news": news,
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json; charset=utf-8")


def set_rss_for_user_test(request):
    user = User.objects.get(username=auth.get_user(request).username)
    portals_user_list = get_user_rss_news(request, user_id=user.id)
    test_new = RssNews.objects.filter(portal_name_id__in=(portals_user_list[i]["portal_id"] for i
                                                          in range(len(portals_user_list)))).values()
    return test_new





def remove_rss_portal_from_feed(request, uuid, pid):
    args = {}
    args.update(csrf(request))
    user = User.objects.get(id=UserProfile.objects.get(uuid=uuid).user_id)
    user_rss_instance = UserRssPortals.objects.get(portal_id=pid, user_id=user.id)
    user_rss_instance.check = False
    user_rss_instance.save()
    rss_portal_instance = RssPortals.objects.get(id=int(pid))
    rss_portal_instance.follows -= 1
    rss_portal_instance.save()
    # portal_news_instance = RssNews.objects.filter(portal_name_id=int(pid))
    # count_news = portal_news_instance.count() # amount of news on this portal
    # list_of_news = portal_news_instance.order_by("-date_posted").values('id')
    # for i in range(count_news):
    #     user_rss_instance = UserRssNewsReading.objects.get(user_id=user.id, rss_news_id=list_of_news[i]['id'])
    #     user_rss_instance.delete()

    data_response = {
        "uuid": str(User.objects.get(username=auth.get_user(request).username).profile.uuid),
        "id": pid
    }
    return HttpResponse(json.dumps(data_response), content_type="application/json")





def save_rss_news(request, rss_id):
    user = User.objects.get(username=auth.get_user(request).username)
    if not RssSaveNews.objects.filter(user_id=user.id).filter(rss_id=rss_id).exists():
        RssSaveNews.objects.create(
            user_id=user.id,
            rss_id=rss_id
        )
    else:
        pass
    return HttpResponse(json.dumps({"process": "added"}), content_type="application/json")


def forget_rss_news(request, rss_id):
    instance = RssSaveNews.objects.get(rss_id=int(rss_id))
    instance.delete()
    return HttpResponse(json.dumps({"process": "removed"}), content_type="application/json")


def get_interesting_news(request):
    interest_news = NewsWatches.objects.all().order_by("-watches").values("news_id")
    return News.objects.filter(id__in=interest_news).values()


def test_rendering(request):
    user = User.objects.get(username=auth.get_user(request).username)
    user_rss_list = UserRssPortals.objects.filter(user_id=user.id).filter(check=True).values("id")
    args = {
        "title": "My news | ",
        "test": set_rss_for_user_test(request),
        "user_rss": get_user_rss_news(request, user_id=user.id),
        "popular_rss": get_most_popular_rss_portals(request)[:9],
        "popular_rss_right": get_most_popular_rss_portals(request)[:3],
        "test_2": RssNews.objects.filter(portal_name_id__in=user_rss_list).values(),
    }
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response("test_rss_news.html", args, context_instance=RequestContext(request))


def render_contacts_page(request):
    from news.forms import SendReportForm
    args = {
        "title": "Contacts |",
        "email": "info@insydia.com",
        "phone": "+7-931-579-06-96",
        "cooperation": "advert@insydia.com",
        "form": SendReportForm,

        "left_bar": True,
    }
    args.update(csrf(request))
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response("contacts.html", args)


def render_about_page(request):
    args = {
        "title": "About |",
        "left_bar": True,
    }
    args.update(csrf(request))
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["expression"] = """We express our gratitude for the financial and moral support to Afanasyev M.J.
(Associate Professor of "Instrumentation Technology")."""
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response("about.html", args)


def render_adertisers_page(request):
    args = {
        "title": "Advertisement | ",

        "left_bar": True,
    }
    args.update(csrf(request))
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = get_news_for_footer(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response("advertisers.html", args)


def set_user_portals(request):
    args = {}
    args.update(csrf(request))
    user = User.objects.get(username=auth.get_user(request).username)
    if request.POST:
        portals_list = request.POST.getlist("portals[]")
        for i in portals_list:
            rss_instance = UserRssPortals.objects.get(user_id=user.id, portal_id=int(i))
            rss_instance.check = True
            rss_instance.save()
    return HttpResponseRedirect("/news/usernews/")


def change_rates(request):
    args = {}
    args.update(csrf(request))
    if request.POST:# or request.is_ajax():
        dataArray = request.POST.getlist("dataArray")
        print(dataArray)
        a = json.loads(dataArray[0])
        for i in range(len(a["dict"])):
            #print("a")
            current_id = int(a["dict"]["%s"%i]["id"][5:])
            current_position = a["dict"]["%s"%i]["pos"]
            #print(i, ": {")
            #print("\tid: ", current_id)
            #print("\tpos: ", current_position)
            #print("}")
            instance = UserRssPortals.objects.get(id=current_id)
            prev_position = instance.position
            instance.position = current_position
            #instance.rate = 1 + (1 * (abs(prev_position-instance.position)/100))
            if abs(instance.position-prev_position) != 0:
                instance.rate = (1 * (((100/instance.position)/abs(instance.position-prev_position))/100)) * (prev_position/instance.position)
            else:
                instance.rate = (1 * (((100/instance.position)/100)) * (prev_position/instance.position))
            instance.save()
    return HttpResponseRedirect("/news/usernews/")


def send_report(request):
    mail_subject = "[REPORT] I have found error"

    import requests
    from django.conf import settings
    response = {}
    data = request.POST
    captcha_rs = data.get('g-recaptcha-response')
    url = "https://www.google.com/recaptcha/api/siteverify"
    params = {
        'secret': settings.NORECAPTCHA_SECRET_KEY,
        'response': captcha_rs,
        #'remoteip': get_client_ip(request)
    }
    verify_rs = requests.get(url, params=params, verify=True)
    verify_rs = verify_rs.json()
    response["status"] = verify_rs.get("success", False)
    response['message'] = verify_rs.get('error-codes', None) or "Unspecified error."

    if response["status"]:
        if request.POST:
            text_content = request.POST["message"] + "\nE-mail: "+request.POST["email"]+"\nName: "+request.POST["username"]
            mail_from = "support@insydia.com"
            mail_to = "support@insydia.com"
            send_mail(mail_subject, text_content, mail_from, [mail_to])

    return HttpResponseRedirect("/about/contacts/")


def page_not_found(request):
    response = render_to_response("404.html", context_instance=RequestContext(request))
    response.status_code = 404
    return response


def change_languages(request, news_id, lang_code):
    instance = News.objects.get(id=news_id)
    if lang_code == 'rus':
        data = instance.news_post_text_russian
    elif lang_code == "eng":
        data = instance.news_post_text_english
    elif lang_code == "ch":
        data = instance.news_post_text_chinese
    else:
        data = "Currently post has not any translation versions."
    response_data = {
        "data": [data],
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def change_languages_top_news(request, news_id, lang_code):
    instance = TopNews.objects.get(id=news_id)
    if lang_code == 'rus':
        data = instance.top_news_post_text_russian
    elif lang_code == "eng":
        data = instance.top_news_post_text_english
    elif lang_code == "ch":
        data = instance.top_news_post_text_chinese
    else:
        data = "Currently post has not any translation versions."
    response_data = {
        "data": [data],
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")



def translate_news_from_top(request):
    instance_news = TopNews.objects.all().last()
    News.objects.create(
        news_title=instance_news.top_news_title,
        news_category_id=instance_news.top_news_category_id,
        news_post_date=instance_news.top_news_post_date,
        news_post_text_english=instance_news.top_news_post_text_english,
        news_post_text_russian=instance_news.top_news_post_text_russian,
        news_post_text_chinese=instance_news.top_news_post_text_chinese,
        news_portal_name=NewsPortal.objects.get(id=instance_news.top_news_portal_name_id),
        news_company_owner=Companies.objects.get(id=instance_news.top_news_company_owner_id),
        news_author=User.objects.get(id=instance_news.top_news_author_id),
        news_main_cover=instance_news.top_news_main_cover,
        news_likes=instance_news.top_news_likes,
        news_dislikes=instance_news.top_news_dislikes
    )
    instance_news.delete()
    return HttpResponseRedirect("http://127.0.0.1:8000/admin/news/topnews/add/")


def get_rss_news_current_portal(request, portal_verbose):
    instance_portal = RssNews.objects.filter(portal_name_id=RssPortals.objects.get(verbose_name=portal_verbose).id)

    response_data = {
        "data": [i.get_json_rss() for i in instance_portal.all()]
    }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def render_current_portal_news(request, portal, template="user_news_beta.html", page_template="current_portal_rss_news.html", extra_context=None):
    try:
        portal_instance = RssPortals.objects.get(verbose_name=portal)

        args = {
            "page_template": page_template,
            "portal": portal_instance,
            "portal_news": RssNews.objects.filter(portal_name_id=portal_instance.id).order_by("-date_posted").defer("author").defer("content_value").values(),

            "left_bar": False,
        }
        args.update(csrf(request))
        if request.is_ajax():
            template = page_template
        args["footer_news"] = get_news_for_footer(request)[:3]
        if "eng" in request.COOKIES.get('lang'):
            args['lang'] = 'eng'
        elif "rus" in request.COOKIES.get('lang'):
            args['lang'] = 'rus'
        elif "ch" in request.COOKIES.get('lang'):
            args['lang'] = 'ch'
        return render_to_response(template, args, context_instance=RequestContext(request))
    except RssPortals.DoesNotExist:
        return page_not_found(request)


def blink_to_company(request, company_name):
    return Companies.objects.get(name=company_name).id


def get_match_company(request, company):
    instanse_all = Companies.objects.filter(Q(name__contains=company) | Q(verbose_name__contains=company))[:10]
    response_data = {
        "data": [i.get_json_company_suggest() for i in instanse_all.all()]
    }
    return HttpResponse(json.dumps([i.get_json_company_suggest() for i in instanse_all.all()]), content_type="application/json")


# def get_company_id(request, company_verbose):
#     word = company_verbose.replace("%20", " ")
#     return HttpResponse(json.dumps({"data": Companies.objects.get(name__contains=word).get_json_company_suggest()}), content_type="application/json")

def get_news_for_footer(request):
    return News.objects.order_by("-news_post_date").defer("news_dislikes").defer("news_likes").defer("news_post_text_english").defer("news_post_text_chinese").defer("news_post_text_russian").defer("news_author").defer("news_portal_name")


@login_required(login_url="/auth/login/")
def render_manager_portal(request):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    args = {
        "username": user_instance,
        "user_rss_portals": get_user_rss_portals(request, user_id=user_instance.id),
        "left_bar": False,
        "here_private": True,
        "footer_news": get_news_for_footer(request)[:3],
    }
    args.update(csrf(request))
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response("manage_portals.html", args, context_instance=RequestContext(request))


def get_all_rss_portals(request):
    return RssPortals.objects.all().values()

@login_required(login_url="/auth/login/")
def render_browser_portals(request, template="browse_portals.html", browse_template="browse_template.html", extra_context=None):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    args = {
        "username": user_instance,
        "browse_template": browse_template,
        "rss_portals": get_all_rss_portals(request),
        "user_rss_portals": get_user_rss_portals(request, user_id=user_instance.id),
        "left_bar": False,
        "here_private": True,
        "browser": True,

        "portals_count": RssPortals.objects.count(),
        "channels_count": RSSChannels.objects.count(),
        "most_popular": RssPortals.objects.order_by("follows")[:12],


        "rss_tech": RssPortals.objects.filter(category_id=1).order_by("-follows")[:4],
        "rss_ent": RssPortals.objects.filter(category_id=2).order_by("-follows")[:4],
        "rss_auto": RssPortals.objects.filter(category_id=3).order_by("-follows")[:4],
        "rss_space": RssPortals.objects.filter(category_id=4).order_by("-follows")[:4],
        "rss_bio": RssPortals.objects.filter(category_id=5).order_by("-follows")[:4],
        "footer_news": get_news_for_footer(request)[:3],
    }
    args.update(csrf(request))

    if request.is_ajax():
        template = browse_template
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response(template, args, context_instance=RequestContext(request))


def render_browse_tech_portals(request, template="browse_tech.html", browse_tech_portals="browse_tech_template.html", extra_context=None):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    args = {
        "username": user_instance,
        "browse_tech_portals": browse_tech_portals,
        "rss_portals": get_all_rss_portals(request),
        "user_rss_portals": get_user_rss_portals(request, user_id=user_instance.id),
        "left_bar": False,
        "here_private": True,


        "rss_tech": RssPortals.objects.filter(category=1).exclude(
            id__in=get_user_rss_portals(request, user_id=user_instance.id).values("portal_id")
        ).order_by("-follows"),
    }
    args.update(csrf(request))

    if request.is_ajax():
        template = browse_tech_portals
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response(template, args, context_instance=RequestContext(request))


def render_close_page(request, lang):
    args = {
        "title": "INSYDIA",
    }
    args.update(csrf(request))

    if lang == "en":
        args["slog"] = "Our service is coming soon!"
        args["about"] = "Insydia is a news providing service. " \
                        "<p>We are focused on categories such as: High-tech, auto," \
                        "<br>aerospace technologies, entertainment and bio-technology. " \
                        "<p>You will be able to read a lot of news which you never" \
                        "<br>read somewhere else. Also, we will gather special articles" \
                        "<br>only for you, that is you can gather your own collection of " \
                        "<br>interesting news and enjoying reading them. And many more... " \
                        "<p>Let's work together and spread news about all companies and"\
                        "<br>achievements all over the World!"
        args["top_one"] = "About"
        args["top_two"] = "Get in touch"
        args["left_item"] = "ABOUT"
        args["right_item"] = "CONTACTS"
        args["contacts"] = "E-mail: support@insydia.com"\
        "<br>Phone: +7-931-579-06-96"\
        "<br>Location: Russia, St. Petersburg"
        args["sub_title"] = "Subscribe"
        args["subs"] = "Subscribe to our newsletter the launch of our service."
        args["subs_success"] = "Thank you for subscriptions. We will send you a message when we get back."
    elif lang == "ru":
        args["slog"] = "Скоро запуск"
        args["about"] = "Проект Insydia - это особый новостной сервис." \
        "<p>Мы ориентированы на такие категории как: Высокие-технологии," \
        "<br>развлечения, авто, космос и био-технологии." \
        "<p>Здесь Вы сможете прочитать такие новости, какие вряд ли сможете" \
        "<br>найти где-либо ещё. Кроме того, мы специально для Вас подготовим" \
        "<br>интересные статьи, чтобы Вы смогли собрать свою уникальную" \
        "<br>коллекцию новостей и наслаждась, читать их. И кое-что ещё..."\
        "<p>Давайте сотрудничать и работать совместо, распространяя новости" \
        "<br>обо всех компаниях и достижениях человечства по всему Миру!"
        args["top_one"] = "О проекте"
        args["top_two"] = "Свяжитесь с нами"
        args["left_item"] = "О НАС"
        args["right_item"] = "КОНТАКТЫ"
        args["contacts"] = "Электронная почта: support@insydia.com"\
        "<br>Телефон: +7-931-579-06-96"\
        "<br>Расположение: Россия, Санкт-Петербург"
        args["sub_title"] = "Подписка"
        args["subs"] = "Подпишитесь на рассылку об открытии нашего сервиса."
        args["subs_success"] = "Спасибо за подписку. Мы сообщим о запуске, отправив Вам сообщение на электронную почту."
    else:
        args["slog"] = "我們的服務即將推出"
        args["about"] = "印度是一個消息提供服務。" \
                        "<p>我們專注於如類：高科技，汽車，航空航天技術，娛樂和生物技術。"\
        "<br>您可以閱讀大量的新聞，你從來沒有看過別的地方。此外，我們將收集特殊物品只為你，" \
        "<p>這是你可以收集你自己收集的有趣的新聞，享受閱讀。 還有很多..."\
        "<p>讓我們攜手合作，傳播新聞的所有公司和成就遍布世界！"
        args["top_one"] = "關於"
        args["top_two"] = "保持聯繫"
        args["left_item"] = "關於"
        args["right_item"] = "聯繫人"
        args["contacts"] = "電子信箱：support@insydia.com"\
        "<br>電話：+7-931-579-06-96"\
        "<br>地點：俄羅斯，聖彼得堡"
        args["sub_title"] = "訂閱新聞"
        args["subs"] = "我們將宣布推出我們的項目通過消息的電子郵件。"
        args["subs_success"] = "感謝您的訂閱。當我們回來，我們會送你一個消息。"

    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response("close_site.html", args)


def check_email_subs(request, email):
    from .models import SubscriptionUsers
    if SubscriptionUsers.objects.filter(email=email).exists():
            return HttpResponse(json.dumps({"data": True}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"data": False}), content_type="application/json")


def closet_subscribe(request):
    from .models import SubscriptionUsers
    import uuid
    args = {}
    args.update(csrf(request))
    if request.POST:
        print("post")
        if not SubscriptionUsers.objects.filter(email=request.POST["email"]).exists():
            SubscriptionUsers.objects.create(
                email=request.POST['email'],
                uid=uuid.uuid3(uuid.NAMESPACE_DNS, "%s" % request.POST["email"])
            )
            return HttpResponse(json.dumps({"data": True}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"data": False}), content_type="application/json")
    return HttpResponse()


def follow_current_rss_portal(request, uuid, pid):
    args = {}
    args.update(csrf(request))
    user = User.objects.get(id=UserProfile.objects.get(uuid=uuid).user_id)
    try:
        user_rss_instance = UserRssPortals.objects.get(portal_id=pid, user_id=user.id)
        if user_rss_instance.check == False:
            user_rss_instance.check = True
            user_rss_instance.save()
            rss_portal_instance = RssPortals.objects.get(id=int(pid))
            rss_portal_instance.follows += 1
            rss_portal_instance.save()
            data = {
                'uuid': str(user.profile.uuid),
                'id': pid
            }
            portal_news_instance = RssNews.objects.filter(portal_name_id=int(pid))
            count_news = portal_news_instance.count() # amount of news on this portal

            list_of_news = portal_news_instance.order_by("-date_posted").values('id')

            for i in range(count_news):
                if i < 5:
                    UserRssNewsReading.objects.create(
                        user_id=user.id,
                        rss_news_id=list_of_news[i]['id'],
                        rss_portal_id=int(pid),
                        read=False
                    )
                else:
                     UserRssNewsReading.objects.create(
                        user_id=user.id,
                        rss_news_id=list_of_news[i]['id'],
                        rss_portal_id=int(pid),
                        read=True
                    )
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            user_rss_instance.check = True
            user_rss_instance.save()
            return HttpResponse(json.dumps({'exists': True}), content_type="application/json")
    except UserRssPortals.DoesNotExist:
        UserRssPortals.objects.create(
            user_id=user.id,
            portal_id=pid,
            check=True,
            position=0,
            rate=0.0
        )
        data = {
            'uuid': str(user.profile.uuid),
            'id': pid
            }
        return HttpResponse(json.dumps(data), content_type="application/json")


def set_current_news_as_read(request, rss_id):
    args = {}
    args.update(csrf(request))
    user_instance = User.objects.get(username=auth.get_user(request).username)
    read_instance = UserRssNewsReading.objects.get(user_id=user_instance.id, rss_news_id=rss_id)
    read_instance.read = True
    read_instance.save()
    return HttpResponse(json.dumps({'read': True}), content_type="application/json")


def count_unread_articles(request, portal_id):
    args = {}
    args.update(csrf(request))
    user_instance = User.objects.get(username=auth.get_user(request).username)
    data = UserRssNewsReading.objects.filter(user_id=user_instance.id).filter(rss_portal_id=portal_id).filter(read=False).count()
    return HttpResponse(json.dumps({'data': data}), content_type="application/json")


def get_rss_matches(request, word):
    args = {}
    args.update(csrf(request))

    instance = RssNews.objects.filter(Q(title__contains=str(word).capitalize()) |
                                      Q(title__contains=str(word).lower()) |
                                      Q(post_text__contains=str(word).capitalize()) |
                                      Q(post_text__contains=str(word).lower()) |
                                      Q(portal_name__portal__contains=str(word).capitalize()) |
                                      Q(portal_name__portal__contains=str(word).lower()) |
                                      Q(portal_name__description__contains=str(word).capitalize()) |
                                      Q(portal_name__description__contains=str(word).lower()) |
                                      Q(content_value__contains=str(word).capitalize())  |
                                      Q(content_value__contains=str(word).lower())).distinct("portal_name__portal")

    return HttpResponse(json.dumps([i.get_portal_json() for i in instance.all()]), content_type="application/json")


def get_current_rss_portal(request, rss_id):
    args = {}
    args.update(csrf(request))

    # portal_id = RssNews.objects.get(id=int(rss_id))[0].portal_name_id

    data_response = {
        'string': """<div id="preview-portal-content" style="border: solid 1px lightgrey; border-radius: 5px;">
                        <div id="ppc-cover" style="width: 350px; height: 150px; background: url('{cover}') no-repeat center; background-size: cover;"></div>
                        <div id="ppc-name"><img src="{favicon}" width="32px" height="32px" /><b>{portal}</b></div>
                        <div id="ppc-description"><i>{description}</i></div>
                        <div id="ppc-params">Followers:&nbsp;{follows}</div>
                        <div id="ppc-follow">
                            <button id="ppc-follow" onclick="followCurrentRssPortal('%s','%s','%s');" class="btn btn-success">Follow</button>
                        </div>
                    </div>""" % (User.objects.get(username=auth.get_user(request).username).profile.uuid, rss_id, rss_id),
        "data": RssPortals.objects.get(id=int(rss_id)).get_portal_full(),
    }

    return HttpResponse(json.dumps(data_response), content_type="application/json")


def search_rss(request):
    from feedfinder2 import find_feeds
    import tldextract
    from .models import RSSChannels
    import lxml.html
    import urllib, urllib.request as r
    from urllib import error
    import uuid
    args = {}
    data_response = {}
    args.update(csrf(request))
    if request.POST:
        url = request.POST['url']
        feeds = find_feeds(url)
        # print(feeds)
        url_instance = tldextract.extract(url)
        url_domain, url_suffix = url_instance.domain, url_instance.suffix

        try:
            favicon = ""
            # home_page_url = "http://"+url_domain+"."+url_suffix


            home_page_url = r.urlopen("http://"+url_domain+"."+url_suffix).__dict__["url"]


            req = urllib.request.Request(home_page_url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 YaBrowser/16.2.0.1818 (beta) Safari/537.36'})
            favicons = lxml.html.parse(r.urlopen(req)).xpath('//link[@rel="shortcut icon"]/@href')
            if len(favicons) > 0:
                favicon = favicons[0]
            if len(favicons) == 0:
                favicons = lxml.html.parse(url).xpath('//link[@rel="icon"]/@href')
                if len(favicons) > 0: favicon = favicons[0]
            elif len(favicons) == 0:
                favicons = lxml.html.parse(url).xpath('//link[@rel="apple-touch-icon-precomposed"]/@href')
                if len(favicons) > 0: favicon = favicons[0]
            elif len(favicon) == 0:
                favicons = lxml.html.parse(url).xpath('//link[@rel="apple-touch-icon"]/@href')
                if len(favicons) > 0: favicon = favicons[0]
            # if len(favicons) == 0:
            #     favicon = ""
            # else:
            #     favicon = favicons[0]
            # if url_domain+"."+url_suffix not in favicon:
            else:
                favicon = ""
            if favicon != '' and 'http' not in favicon:
                favicon = home_page_url+favicon
            # if favicon[:2] == '//':
            #     favicon = str(favicons[0])[2:]
            # else:
            #     favicon = "%sfavicon.ico" % url
        except OSError or urllib.error.HTTPError:
            favicon = ""



        ##################### GET DESCRIPTION ############################
        description = ""
        try:
            "http://www.useragentstring.com/"
            # url = url_domain+"."+url_suffix
            # home_page_url = "http://"+url_domain+"."+url_suffix


            home_page_url = r.urlopen("http://"+url_domain+"."+url_suffix).__dict__["url"]


            req = urllib.request.Request(home_page_url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 YaBrowser/16.2.0.1818 (beta) Safari/537.36'})
            description = lxml.html.parse(r.urlopen(req)).xpath('//meta[@name="description"]//@content')
            if len(description)>0:description=description[0]
            if description == '':
                description = lxml.html.parse(r.urlopen(req)).xpath('//title')[0].text
            if description == '':
                description = lxml.html.parse(r.urlopen(req)).xpath('//meta[@name="twitter:description"]//@content')[0]
        except urllib.error.HTTPError:
            description = ""
        ################### END GETTING DESCRIPTION #######################



        if RssPortals.objects.filter(portal_base_link=str(url_domain+"."+url_suffix), portal=str(url_domain).capitalize(), verbose_name=url_domain).exists() == False:
            if feeds:
                RssPortals.objects.create(
                    portal=str(url_domain).capitalize(),
                    portal_base_link=url_domain+"."+url_suffix,
                    follows=0,
                    description=description,
                    cover="",
                    favicon=favicon,
                    verbose_name=url_domain,
                    category_id=1,
                    puid=uuid.uuid3(uuid.NAMESPACE_DNS, "%s" % str(url_domain+"."+url_suffix))
                )
                if RssPortals.objects.get(portal_base_link=url_domain+"."+url_suffix).favicon == '':
                    send_mail_about_favicon(request, str(url_domain+"."+url_suffix))
                for i in feeds:
                    if 'comment' not in i:
                        RSSChannels.objects.create(
                            portal_id=RssPortals.objects.get(portal=str(url_domain).capitalize()).id,
                            link=i
                        )
        else:
            data_response['pid'] = RssPortals.objects.get(portal=str(url_domain).capitalize()).id
            data_response['exists'] = True
            pass
        if len(feeds) > 0:
            data_url = True
            data_response["data"] = data_url
            data_response["feed"] = feeds
            data_response['response'] = True
        else:
            data_response['response'] = False

        return HttpResponse(json.dumps(data_response), content_type="application/json")
    else:
        raise 404


def send_mail_about_favicon(request, portal):
    from django.conf import settings

    subject = "[FAVICON] Didn't load favicon"
    body = """Didn't load favicon of %s via user "Browser Portal"
    """ % (portal)

    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
    return HttpResponse(json.dumps({'report': 'send'}), content_type="application/json")


def aggregate_current_feeds(request):
    from feedfinder2 import find_feeds
    from .aggregator import Aggregator
    if request.POST:
        url = request.POST['url']
        feeds = find_feeds(url)
        Aggregator(urls=feeds)
        return HttpResponse(json.dumps({'end': 'true'}), content_type="application/json")



def get_latest_articles_of_new_rss(request):
    from .models import RSSChannels
    import tldextract
    args = {}
    args.update(csrf(request))
    if request.POST:
        url = request.POST['url']
        url_instance = tldextract.extract(url)
        url_domain = str(url_instance.domain).capitalize()
        pid = RssPortals.objects.get(portal=url_domain).id

        instance = RssNews.objects.filter(portal_name_id=pid).order_by("-date_posted")[0].get_json_rss()

        data_response = {
            "data": instance,
        }

        return HttpResponse(json.dumps(data_response), content_type="application/json")


def popup_current_portal(request, portal_id):
    args = {}
    args.update(csrf(request))

    l = request.COOKIES.get("lang")
    b = ""
    if l == "eng": b = "By"
    elif l == "ch": b = "ch"
    elif l == "rus": b = "Автор"


    instance = RssPortals.objects.get(id=portal_id)
    # news_instance = RssNews.objects.filter(portal_name_id=portal_id)
    translation = {
        "id": "id",
        "title": "title",
        "date_posted": "date_posted",
        "portal_name_id": "portal_name_id",
        "author": "author",
        "nuid": "nuid"
    }
    news_instance = list(RssNews.objects.raw("SELECT id, title, date_posted, portal_name_id, author, nuid FROM news_rss WHERE portal_name_id=%s" % portal_id, translations=translation))

    news_instance_offset = news_instance[:12]
    string_offset = """<div class="cur-pw-articles">
<ul class="cur-pw-item" style="padding-left: 0;">"""
    for i in news_instance_offset:
        string_offset += """
    <li class="col-xs-12" style="height:200px;border-bottom: solid 1px lightgrey;">
        <div class="cur-pw-ar">
            <div class="cur-pw-ar-cover col-md-3">
                <div class="cont-cover" onclick="loadCurrentArticle('%s');return false;" style="background: url('%s') no-repeat center; background-size: cover;"></div>
            </div>
            <div class="cur-pw-ar-content col-md-9">
                <div class="cur-pw-ar-t" onclick="loadCurrentArticle('%s'); return false;">%s</div>
                <div class="cur-pw-ar-par" style="font-size:14px;">
                    %s&nbsp;<span style="color: #F62A00;">%s</span>
                    &nbsp;|&nbsp;
                    <span>%s</span>
                </div>
            </div>
        </div>
    </li>
""" % (i.id,
       i.get_main_cover(),
       i.id,
       i.title,
       b,
       i.author,
       i.date_posted.strftime("%b, %d %Y"))
    string_offset+="""</ul></div>"""
    string = """<div class="cur-pw-top">
<div class="cur-pw-background"></div>
<div class="cur-pw-btn-bck"></div>

<div class="cur-pw-btn-bck">
    <button class="btn-close-rss btn btn-primary" onclick="hideCurrentRssPortal();return false;">Close</button>
</div>

"""

    if UserRssPortals.objects.get(portal_id=portal_id, user_id=User.objects.get(username=auth.get_user(request).username).id).check == False or\
        UserRssPortals.objects.get(portal_id=portal_id, user_id=User.objects.get(username=auth.get_user(request).username)).DoesNotExist:
        string += """<div class="cur-pw-btn-fl" data-id="{id}" data-special-id="{uuid}">
        <button class="btn-fl-rss btn btn-primary" onclick="followCurrentRssPortal('{uuid}', '{id}', '{id}');
            return false;">Follow</button>
    </div>
    """.format(uuid=str(User.objects.get(username=auth.get_user(request).username).profile.uuid),
               id=instance.id)
    else:
        string += """<div class="cur-pw-btn-fl" data-id="{id}" data-special-id="{uuid}">
        <button class="btn-fl-rss btn btn-primary" onclick="unfollowCurrentRssPortal('{uuid}', '{id}', '{id}'); return
        false;">Unfollow</button></div>""".\
            format(uuid=str(User.objects.get(username=auth.get_user(request).username).profile.uuid),
                   id=instance.id)

    string += """<div class="cur-pw-description col-md-12" style="position: absolute; top: 3em;">
        <h1 class="text-center">%s</h1>
        <div class="cur-pw-td text-center">%s</div>
    </div>
        <div class="cur-pw-right text-center col-xs-6 col-xs-offset-3">
            <span class="cur-pw-follows">Followers: %s</span>&nbsp;|&nbsp;
            <span class="cur-pw-articles-amount">Articles: %s</span>
        </div>
</div>
</div>
<div class="cur-pw-left col-md-12">
    %s
</div>
    """ % (instance.portal,
           instance.description,
           instance.follows,
           len(news_instance),
           string_offset)


    data_response = {
        "data": string,
    }

    return HttpResponse(json.dumps(data_response), content_type="application/json")

def popup_current_portal_mobile(request, portal_id):
    args = {}
    args.update(csrf(request))

    l = request.COOKIES.get("lang")
    b = ""
    if l == "eng": b = "By"
    elif l == "ch": b = "ch"
    elif l == "rus": b = "Автор"


    instance = RssPortals.objects.get(id=portal_id)
    # news_instance = RssNews.objects.filter(portal_name_id=portal_id)
    translation = {
        "id": "id",
        "title": "title",
        "date_posted": "date_posted",
        "portal_name_id": "portal_name_id",
        "author": "author",
        "nuid": "nuid"
    }
    news_instance = list(RssNews.objects.raw("SELECT id, title, date_posted, portal_name_id, author, nuid FROM news_rss WHERE portal_name_id=%s" % portal_id, translations=translation))

    news_instance_offset = news_instance[:12]
    string_offset = """<div class="cur-pw-articles">
<ul class="cur-pw-item" style="padding-left: 0;">"""
    for i in news_instance_offset:
        string_offset += """
    <li class="col-xs-12" style="height:200px;border-bottom: solid 1px lightgrey;">
        <div class="cur-pw-ar">
            <div class="cur-pw-ar-cover col-md-3">
                <div class="cont-cover" onclick="loadCurrentArticle('%s');return false;" style="background: url('%s') no-repeat center; background-size: cover;"></div>
            </div>
            <div class="cur-pw-ar-content col-md-9">
                <div class="cur-pw-ar-t" onclick="loadCurrentArticle('%s'); return false;">%s</div>
                <div class="cur-pw-ar-par" style="font-size:14px;">
                    %s&nbsp;<span style="color: #F62A00;">%s</span>
                    &nbsp;|&nbsp;
                    <span>%s</span>
                </div>
            </div>
        </div>
    </li>
""" % (i.id,
       i.get_main_cover(),
       i.id,
       i.title,
       b,
       i.author,
       i.date_posted.strftime("%b, %d %Y"))
    string_offset+="""</ul></div>"""
    string = """<div class="cur-pw-top">
<div class="cur-pw-background"></div>
<div class="cur-pw-btn-bck"></div>

<div class="cur-pw-btn-bck">
    <button class="btn-close-rss btn btn-primary" onclick="hideCurrentRssPortal();return false;">Close</button>
</div>

"""

    if UserRssPortals.objects.get(portal_id=portal_id, user_id=User.objects.get(username=auth.get_user(request).username).id).check == False or\
        UserRssPortals.objects.get(portal_id=portal_id, user_id=User.objects.get(username=auth.get_user(request).username)).DoesNotExist:
        string += """<div class="cur-pw-btn-fl" data-id="{id}" data-special-id="{uuid}">
        <button class="btn-fl-rss btn btn-primary" onclick="followCurrentRssPortal('{uuid}', '{id}', '{id}');
            return false;">Follow</button>
    </div>
    """.format(uuid=str(User.objects.get(username=auth.get_user(request).username).profile.uuid),
               id=instance.id)
    else:
        string += """<div class="cur-pw-btn-fl" data-id="{id}" data-special-id="{uuid}">
        <button class="btn-fl-rss btn btn-primary" onclick="unfollowCurrentRssPortal('{uuid}', '{id}', '{id}'); return
        false;">Unfollow</button></div>""".\
            format(uuid=str(User.objects.get(username=auth.get_user(request).username).profile.uuid),
                   id=instance.id)

    string += """<div class="cur-pw-description col-md-12" style="position: absolute; top: 0;">
        <h1 class="text-center">%s</h1>
        <div class="cur-pw-td text-center">%s</div>
    </div>
        <div class="text-center col-xs-6 col-xs-offset-3" style="bottom:5px;font-size:10px;color: white; position:absolute;text-clign:center;">
            <span class="cur-pw-follows">Followers: %s</span>&nbsp;|&nbsp;
            <span class="cur-pw-articles-amount">Articles: %s</span>
        </div>
</div>
</div>
<div class="cur-pw-left col-md-12">
    %s
</div>
    """ % (instance.portal,
           instance.description,
           instance.follows,
           len(news_instance),
           string_offset)


    data_response = {
        "data": string,
    }

    return HttpResponse(json.dumps(data_response), content_type="application/json")



def render_catalog(request):
    args = {
        "username":User.objects.get(username=auth.get_user(request).username),
        "rss_tech": RssPortals.objects.filter(category_id=1).order_by("-follows")[:12],
        "footer_news": get_news_for_footer(request)[:3],
    }
    args.update(csrf(request))
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return render_to_response("catalog.html", args, context_instance=RequestContext(request))


def render_current_category_portals(request, category_id):
    args = {}
    args.update(csrf(request))
    news_instance = RssPortals.objects.filter(category_id=int(category_id)).order_by("-follows")


    string="""<div class="portals-list">
    """

    for i in news_instance:
        string += """<div onclick="showCurrentPortalData('%s'); return false;" class="fadeandscale_open current-popular-portal col-md-2" id="portal-%s" data-alt-id="%s">
                <a href="">
                    <div class="portal-picture" style="background: url('%s') no-repeat center; background-size: cover;"></div>
                </a>
                <div class="portal-bottom">
                    <span class="portal-logo">%s</span>
                    <span class="portal-name">
                        <a href="" class="portal-link">
                            <h3>%s</h3>
                        </a>
                    </span>
                </div>
                <div class="portal-footer">
                    <span class="">Followers:&nbsp;%s</span>&nbsp;|&nbsp;
                    <span class="">Articles:&nbsp;%s</span>
                </div>
            </div>
        """ % (i.id,
               i.id,
               i.puid,
               i.cover,
               i.favicon,
               i.portal,
               i.follows,
               len(list(RssNews.objects.raw("SELECT id FROM news_rss WHERE category_id=%s and portal_name_id=%s" % (category_id, i.id)))))

    string += "</div>"

    data_response = {
        "data": [i.get_portal_full for i in news_instance.all()],
        "string": string,
    }
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return HttpResponse(json.dumps({"data": string}), content_type="application/json")


def render_current_category_portals_mobile(request, category_id):
    args = {}
    args.update(csrf(request))
    news_instance = RssPortals.objects.filter(category_id=int(category_id)).order_by("-follows")


    string="""<div class="portals-list">
    """

    for i in news_instance:
        string += """<div onclick="showCurrentPortalData('%s'); return false;" class="col-xs-6 fadeandscale_open mobile-current-popular-portal col-md-2" id="portal-%s" data-alt-id="%s">
                <a href="">
                    <div class="portal-picture" style="background: url('%s') no-repeat center; background-size: cover;"></div>
                </a>
                <div class="mobile-portal-bottom">
                    <span class="portal-logo">%s</span>
                    <span class="mobile-portal-name">
                        <a href="" class="portal-link">
                            <h3>%s</h3>
                        </a>
                    </span>
                </div>
                <div class="mobile-portal-footer">
                    <span class="">Followers:&nbsp;%s</span>&nbsp;|&nbsp;
                    <span class="">Articles:&nbsp;%s</span>
                </div>
            </div>
        """ % (i.id,
               i.id,
               i.puid,
               i.cover,
               i.favicon,
               i.portal,
               i.follows,
               len(list(RssNews.objects.raw("SELECT id FROM news_rss WHERE category_id=%s and portal_name_id=%s" % (category_id, i.id)))))

    string += "</div>"

    data_response = {
        "data": [i.get_portal_full for i in news_instance.all()],
        "string": string,
    }
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    return HttpResponse(json.dumps({"data": string}), content_type="application/json")



def popup_new_portal(request):
    import tldextract
    args = {}
    args.update(csrf(request))

    l = request.COOKIES.get("lang")
    b = ""
    if l == "eng": b = "By"
    elif l == "ch": b = "ch"
    elif l == "rus": b = "Автор"

    if request.POST:
        url = request.POST['url']
        url_instance = tldextract.extract(url)
        url_domain = url_instance.domain
        portal_id = RssPortals.objects.get(portal=str(url_domain).capitalize()).id

        instance = RssPortals.objects.get(id=portal_id)
        news_instance = RssNews.objects.filter(portal_name_id=portal_id)

        news_instance_offset = news_instance[:12]
        string_offset = """<div class="cur-pw-articles">
    <ul class="cur-pw-item" style="padding-left: 0;">"""
        for i in news_instance_offset:
            string_offset += """
        <li class="col-xs-12" style="height:120px;border-bottom: solid 1px lightgrey;">
            <div class="cur-pw-ar">
                <div class="cur-pw-ar-cover col-md-3">
                    <div class="cont-cover" onclick="loadCurrentArticle('%s');return false;" style="background: url('%s') no-repeat center; background-size: cover;"></div>
                </div>
                <div class="cur-pw-ar-content col-md-9">
                    <div class="cur-pw-ar-t" onclick="loadCurrentArticle('%s'); return false;">%s</div>
                    <div class="cur-pw-ar-par">
                        %s&nbsp;<span style="color: #F62A00;">%s</span>
                        &nbsp;|&nbsp;
                        <span>%s</span>
                    </div>
                </div>
            </div>
        </li>
    """ % (i.id,
           i.get_main_cover(),
           i.id,
           i.title,
           b,
           i.author,
           i.date_posted.strftime("%b, %d %Y"))
        string_offset+="""</ul></div>"""
        string = """<div class="cur-pw-top">
    <div class="cur-pw-background"></div>
    <div class="cur-pw-btn-bck"></div>"""

        if UserRssPortals.objects.filter(portal_id=portal_id, user_id=User.objects.get(username=auth.get_user(request).username).id).exists() == False or\
            UserRssPortals.objects.get(portal_id=portal_id, user_id=User.objects.get(username=auth.get_user(request).username)).DoesNotExist:
            string += """<div class="cur-pw-btn-fl" data-id="{id}" data-special-id="{uuid}">
            <button class="btn-fl-rss btn btn-primary" onclick="followCurrentRssPortal('{uuid}', '{id}', '{id}');
                return false;">Follow</button>
        </div>
        """.format(uuid=str(User.objects.get(username=auth.get_user(request).username).profile.uuid),
                   id=instance.id)
        else:
            string += """<div class="cur-pw-btn-fl" data-id="{id}" data-special-id="{uuid}">
            <button class="btn-fl-rss btn btn-primary" onclick="unfollowCurrentRssPortal('{uuid}', '{id}', '{id}'); return
            false;">Unfollow</button></div>""".\
                format(uuid=str(User.objects.get(username=auth.get_user(request).username).profile.uuid),
                       id=instance.id)

        string += """<div class="cur-pw-description col-md-12" style="position: absolute; top: 3em;">
            <h1 class="text-center">%s</h1>
            <div class="cur-pw-td text-center">%s</div>
        </div>
            <div class="cur-pw-right text-center col-xs-6 col-xs-offset-3">
                <span class="cur-pw-follows">Followers: %s</span>&nbsp;|&nbsp;
                <span class="cur-pw-articles-amount">Articles: %s</span>
            </div>
    </div>
    </div>
    <div class="cur-pw-left col-md-12">
        %s
    </div>
        """ % (instance.portal,
               instance.description,
               instance.follows,
               news_instance.count(),
               string_offset)


        data_response = {
            "data": string,
        }

        return HttpResponse(json.dumps(data_response), content_type="application/json")
    else:
        return HttpResponse()


def popup_new_portal_mobile(request):
    import tldextract
    args = {}
    args.update(csrf(request))

    l = request.COOKIES.get("lang")
    b = ""
    if l == "eng": b = "By"
    elif l == "ch": b = "ch"
    elif l == "rus": b = "Автор"

    if request.POST:
        url = request.POST['url']
        url_instance = tldextract.extract(url)
        url_domain = url_instance.domain
        portal_id = RssPortals.objects.get(portal=str(url_domain).capitalize()).id

        instance = RssPortals.objects.get(id=portal_id)
        news_instance = RssNews.objects.filter(portal_name_id=portal_id)

        news_instance_offset = news_instance[:12]
        string_offset = """<div class="cur-pw-articles">
    <ul class="cur-pw-item" style="padding-left: 0;">"""
        for i in news_instance_offset:
            string_offset += """
        <li class="col-xs-12" style="height:120px;border-bottom: solid 1px lightgrey;">
            <div class="cur-pw-ar">
                <div class="cur-pw-ar-cover col-md-3">
                    <div class="cont-cover" onclick="loadCurrentArticle('%s');return false;" style="background: url('%s') no-repeat center; background-size: cover;"></div>
                </div>
                <div class="cur-pw-ar-content col-md-9">
                    <div class="cur-pw-ar-t" onclick="loadCurrentArticle('%s'); return false;">%s</div>
                    <div class="cur-pw-ar-par">
                        %s&nbsp;<span style="color: #F62A00;">%s</span>
                        &nbsp;|&nbsp;
                        <span>%s</span>
                    </div>
                </div>
            </div>
        </li>
    """ % (i.id,
           i.get_main_cover(),
           i.id,
           i.title,
           b,
           i.author,
           i.date_posted.strftime("%b, %d %Y"))
        string_offset+="""</ul></div>"""
        string = """<div class="cur-pw-top">
<div class="cur-pw-background"></div>
<div class="cur-pw-btn-bck"></div>

<div class="cur-pw-btn-bck">
    <button class="btn-close-rss btn btn-primary" onclick="hideCurrentRssPortal();return false;">Close</button>
</div>

"""
        if UserRssPortals.objects.filter(portal_id=portal_id, user_id=User.objects.get(username=auth.get_user(request).username).id).exists() == False or\
            UserRssPortals.objects.get(portal_id=portal_id, user_id=User.objects.get(username=auth.get_user(request).username)).DoesNotExist:
            string += """<div class="cur-pw-btn-fl" data-id="{id}" data-special-id="{uuid}">
            <button class="btn-fl-rss btn btn-primary" onclick="followCurrentRssPortal('{uuid}', '{id}', '{id}');
                return false;">Follow</button>
        </div>
        """.format(uuid=str(User.objects.get(username=auth.get_user(request).username).profile.uuid),
                   id=instance.id)
        else:
            string += """<div class="cur-pw-btn-fl" data-id="{id}" data-special-id="{uuid}">
            <button class="btn-fl-rss btn btn-primary" onclick="unfollowCurrentRssPortal('{uuid}', '{id}', '{id}'); return
            false;">Unfollow</button></div>""".\
                format(uuid=str(User.objects.get(username=auth.get_user(request).username).profile.uuid),
                       id=instance.id)

        string += """<div class="cur-pw-description col-md-12" style="position: absolute; top: 0;">
        <h1 class="text-center">%s</h1>
        <div class="cur-pw-td text-center">%s</div>
    </div>
        <div class="text-center col-xs-6 col-xs-offset-3" style="bottom:5px;font-size:10px;color: white; position:absolute;text-clign:center;">
            <span class="cur-pw-follows">Followers: %s</span>&nbsp;|&nbsp;
            <span class="cur-pw-articles-amount">Articles: %s</span>
        </div>
</div>
</div>
<div class="cur-pw-left col-md-12">
    %s
</div>
        """ % (instance.portal,
               instance.description,
               instance.follows,
               news_instance.count(),
               string_offset)


        data_response = {
            "data": string,
        }

        return HttpResponse(json.dumps(data_response), content_type="application/json")
    else:
        return HttpResponse()


def render_job_page(request):
    args={}
    args.update(csrf(request))
    response=render_to_response("hire.html", args, context_instance=RequestContext(request))
    response.status_code=200
    return response