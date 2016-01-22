# -*-coding: utf-8 -*-

from django.shortcuts import render_to_response, RequestContext
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import Q
from .models import News, NewsCategory, Companies, TopVideoContent, RssNews, RssPortals, NewsComments, NewsWatches, NewsCommentsReplies, RssNewsCovers, TopNews, NewsPortal,UserRssNewsReading
import datetime
import json
from userprofile.models import UserLikesNews, UserSettings, UserProfile, UserRssPortals
from .forms import NewsCommentsForm, NewsCommentsRepliesForm
from django.core.mail import send_mail
from favourite.models import RssSaveNews

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


def main_page_load(request, template="index_new.html", page_template="page_template.html", extra_context=None):
# def main_page_load(request, template="index_new.html", page_template="page_template.html", extra_context=None, translate="english"):
    args = {
        #test "video_first": TopVideoContent.objects.all().values()[0],
        #test "video_top": TopVideoContent.objects.all().values()[1:3],
        "current_year": datetime.datetime.now().year,
        "title": "Home Page | ",
        "news_block": True,
        # "breaking_news": render_news_by_sendec(request).order_by("-news_post_date")[0],
        "total_middle_news": render_news_by_sendec(request).order_by("-news_post_date")[0:4],
        "total_bottom_news": render_news_by_sendec(request).order_by("-news_post_date")[4:6],
        # "interest": get_interesting_news(request)[:3],
        "interest": get_hottest_news(request),
        "test_ids": NewsWatches.objects.order_by("-watches").values("news_id")[:4],


        "before_reviews": render_news_by_sendec(request).order_by("-news_post_date")[6:9],

        "total_news": get_total_news,
        "page_template": page_template,
        "top_news": get_top_total_news(request),
        #test "latest_review": get_latest_reviews(request),
        "left_bar": True,
    }
    # if translate == "russian":
    #     args["translate"] = "ru"
    # if render_news_by_sendec(request).order_by("-news_post_date")[4:13].count() > 0:
    #     args["total_bottom_news"] = render_news_by_sendec(request).order_by("-news_post_date")[4:13]

    if request.is_ajax():
        template = page_template

    args.update(csrf(request))
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = get_news_for_footer(request)[:3]
    response = render_to_response([template, "footer.html"], context=args, context_instance=RequestContext(request))
    # response.set_cookie("translate-version", translate)
    return response


def get_latest_reviews(request):
    return News.objects.filter(news_category_id=6).order_by("-news_post_date").values()[0]


def get_hottest_news(request):
    # try:
    watches = NewsWatches.objects.order_by("-watches").values("news_id").values("news_id")
    if watches.count() >= 4:
        return News.objects.filter(id__in=watches[:4]).defer("news_portal_name").defer("news_post_text_chinese").defer("news_post_text_russian").defer("news_post_text_english").defer("news_author").values()
    else:
        return News.objects.all().defer("news_post_text_chinese").defer("news_post_text_russian").defer("news_post_text_english").order_by("news_post_date").values()[:4]


def get_top_total_news(request):
    return TopNews.objects.all()[:4].defer("top_news_post_text_english").defer("top_news_post_text_russian").defer("top_news_post_text_chinese").values()


def get_total_news():
    return News.objects.all().order_by("-news_post_date").defer("news_post_text_english").defer("news_post_text_russian").defer("news_post_text_chinese").values()[9:]


def render_news_by_sendec(request, **kwargs):
    if len(kwargs) > 0:
        return News.objects.all().filter(news_category_id=kwargs["category_id"]).exclude(id=kwargs["news_id"]).values()
    else:
        return News.objects.all().values()


def get_company_news(request, news_id, company_id):
    current_company_news = News.objects.filter(news_company_owner=
                                               company_id).exclude(id=news_id).order_by("-news_post_date")
    return current_company_news


def get_latest_news_total(request):
    latest_10_news = News.objects.all().order_by("-news_post_date")
    return latest_10_news


def render_current_top_news(request, category_id, news_id):
    current_news = TopNews.objects.get(id=news_id)
    args = {
        "title": "%s | " % current_news.top_news_title,
        "current_news_values": current_news,
        "other_materials": render_news_by_sendec(request, news_id=news_id,
                                                 category_id=category_id).exclude(id=news_id)[:3],
        "other_materials_count": render_news_by_sendec(request, news_id=news_id,
                                                 category_id=category_id).exclude(id=news_id)[:3].count(),
        "latest_news": get_company_news(request, news_id, current_news.top_news_company_owner_id)[:5],
        "company_name": str(Companies.objects.get(id=current_news.top_news_company_owner_id)).capitalize(),
        "current_day": datetime.datetime.now().day,
        "comments_total": comments_load(request, news_id),
        "replies_total": replies_load(request, news_id),
        "liked": check_like(request, news_id),
        "disliked": check_dislike(request, news_id),
        "like_amount": UserLikesNews.objects.filter(news_id=news_id).filter(like=True).count(),
        "dislike_amount": UserLikesNews.objects.filter(news_id=news_id).filter(dislike=True).count(),
        "current_news_title": current_news.top_news_title,
        #"external_link": shared_news_link(request, news_id),
        "left_bar": True,
    }

    args.update(check_english(current_news, flag=1))

    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    # addition_news_watches(request, news_id)
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response("top_news.html", args)


def render_current_news(request, category_id, news_id):
    current_news = News.objects.get(id=news_id)
    args = {
        "title": "%s | " % current_news.news_title,
        "current_news_values": current_news,
        "other_materials": render_news_by_sendec(request, news_id=news_id,
                                                 category_id=category_id).exclude(id=news_id)[:3],
        "other_materials_count": render_news_by_sendec(request, news_id=news_id,
                                                 category_id=category_id).exclude(id=news_id)[:3].count(),
        "latest_news": get_company_news(request, news_id, current_news.news_company_owner_id)[:5],
        "company_name": str(Companies.objects.get(id=current_news.news_company_owner_id)).capitalize(),
        "current_day": datetime.datetime.now().day,
        "comments_total": comments_load(request, news_id),
        "replies_total": replies_load(request, news_id),
        "liked": check_like(request, news_id),
        "disliked": check_dislike(request, news_id),
        "like_amount": UserLikesNews.objects.filter(news_id=news_id).filter(like=True).count(),
        "dislike_amount": UserLikesNews.objects.filter(news_id=news_id).filter(dislike=True).count(),
        "current_news_title": current_news.news_title,
        #"external_link": shared_news_link(request, news_id),
        "left_bar": True,
    }

    args.update(check_english(current_news, flag=0))

    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    addition_news_watches(request, news_id)
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response("current_news.html", args)


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
def render_user_news(request, template="user_news.html", rss_template="rss_template.html", extra_context=None):
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
                       "<p>You are our <b>HERO</b>, man!</p>", "new_user_news": get_rss_filterd(request, user.id),
            "user_rss_portals": get_user_rss_portals(request, user_id=user.id),
            "left_bar": False,
            "here_private": True,
            "rss_tech": RssPortals.objects.filter(category=1).order_by("-follows")[:4],
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
        return render_to_response(template, context=args, context_instance=RequestContext(request))


def get_rss_filterd(request, user_id):
    user_portals_ids = UserRssPortals.objects.filter(user_id=user_id).filter(check=True).order_by("position").values("portal_id")
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
    instance = RssNews.objects.get(id=int(news_id)).get_json_rss()
    response_data = {
        "data": instance,
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


@login_required(login_url="/auth/login/")
def addition_news_watches(request, news_id):
    instance = NewsWatches.objects.filter(news_id=news_id)
    if instance.exists() and isinstance(instance, News):
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
    return render_to_response("current_category.html", args)

#   ###########################################################################
#   ############################# CATEGORIES ##################################
#   ###########################################################################


def render_technology_news(request, template="technology.html", tech_template="tech_template.html", extra_context=None):
    args = {
        "title": "Technology | ",
        "category_title": "TECHNOLOGY",

        "top_news": get_top_category_news(request, category_name="Technology"),
        "total_middle_news": get_category_news_offset(request, category_name="Technology")[1:5],
        "total_bottom_news": get_category_news_offset(request, category_name="Technology")[5:7],
        "interest": get_category_news_offset(request, category_name="Technology")[7:11],

        "tech_template": tech_template,
        "total_news": get_category_news_offset(request, category_name="Technology")[11:],

        "left_bar": True,
        "here_tech": True,
    }
    if request.is_ajax():
        template = tech_template

    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response(template, args, context_instance=RequestContext(request))


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
    args = {
        "title": "Auto | ",
        "category_title": "AUTO",

        "top_news": get_top_category_news(request, category_name="Auto"),
        "total_middle_news": get_category_news_offset(request, category_name="Auto")[1:5],
        "total_bottom_news": get_category_news_offset(request, category_name="Auto")[5:7],
        "interest": get_category_news_offset(request, category_name="Auto")[7:11],

        "auto_template": auto_template,
        "total_news": get_category_news_offset(request, category_name="Auto")[11:],

        "left_bar": True,
        "here_auto": True,
    }
    if request.is_ajax():
        template = auto_template

    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response(template, args, context_instance=RequestContext(request))


def get_auto_news(request):
    return News.objects.all().filter(news_category_id=NewsCategory.objects.get(category_name="Auto").id)
#   ################################## END AUTO #########################################


def render_bio_news(request, template="bio.html", bio_template="bio_template.html", extra_context=None):
    args = {
        "title": "Bio Technology | ",
        "category_title": "Bio Technology",
        "top_news": get_top_category_news(request, category_name="BIO"),
        "total_middle_news": get_category_news_offset(request, category_name="BIO")[1:5],
        "total_bottom_news": get_category_news_offset(request, category_name="BIO")[5:7],
        "interest": get_category_news_offset(request, category_name="BIO")[7:11],

        "bio_template": bio_template,
        "total_news": get_category_news_offset(request, category_name="BIO")[11:],

        "left_bar": True,
        "here_bio": True,
    }
    if request.is_ajax():
        template = bio_template

    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response(template, args, context_instance=RequestContext(request))


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
    return render_to_response(template, args, context_instance=RequestContext(request))


def get_companies(request):
    return Companies.objects.all().order_by("id").defer("description").defer("site").defer("category")


def render_current_company(request, company_name, template="current_company.html", company_news="current_company_news.html", extra_context=None):
    company = Companies.objects.get(verbose_name=company_name)
    args = {
        "title": company.name+" | ",
        "company": company,
        "company_news": company_news,
        "news": get_companies_news(request, company.id),

        "left_bar": True,
    }
    args.update(csrf(request))

    if request.is_ajax():
        template = company_news

    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response(template, args, context_instance=RequestContext(request))


def get_companies_news(request, company_id):
    return News.objects.filter(news_company_owner_id=company_id).order_by("-news_post_date").values()


#   #############################END COMPANIES###################################


def render_entertainment_news(request, template="entertainment.html", ent_template="ent_template.html", extra_context=None):
    args = {
        "title": "Entertainment | ",
        "category_title": "ENTERTAINMENT",
        "category_flag": "ent",

        "top_news": get_top_category_news(request, category_name="Entertainment"),
        "total_middle_news": get_category_news_offset(request, category_name="Entertainment")[1:5],
        "total_bottom_news": get_category_news_offset(request, category_name="Entertainment")[5:7],
        "interest": get_category_news_offset(request, category_name="Entertainment")[7:11],

        "ent_template": ent_template,
        "total_news": get_category_news_offset(request, category_name="Entertainment")[11:],

        "left_bar": True,
        "here_ent": True,
    }
    if request.is_ajax():
        template = ent_template

    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response(template, args, context_instance=RequestContext(request))


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
    return render_to_response("reviews.html", args)


def render_space_news(request, template="space.html", space_template="space_template.html", extra_context=None):
    args = {
        "title": "Space | ",
        "category_title": "SPACE",
        "top_news": get_top_category_news(request, category_name="Space"),
        "total_middle_news": get_category_news_offset(request, category_name="Space")[1:5],
        "total_bottom_news": get_category_news_offset(request, category_name="Space")[5:7],
        "interest": get_category_news_offset(request, category_name="Space")[7:11],

        "space_template": space_template,
        "total_news": get_category_news_offset(request, category_name="Space")[11:],

        "left_bar": True,
        "here_space": True,
    }
    if request.is_ajax():
        template = space_template

    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args.update(csrf(request))
    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response(template, args, RequestContext(request))


def get_space_news(request):
    return News.objects.all().filter(news_category_id=NewsCategory.objects.get(category_name="Space").id)


#   ################################### END SPACE ##############################3


@login_required(login_url="/auth/login")
def comment_send(request, category_id, news_id):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    args = {
        "username": user_instance,
    }
    args.update(csrf(request))
    if request.POST:
        form = NewsCommentsForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news_attached = News.objects.get(id=news_id)
            comment.comments_author = user_instance
            form.save()
    return HttpResponseRedirect("/news/%s/%s/" % (category_id, news_id), args)


def comments_load(request, news_id):
    return NewsComments.objects.filter(news_attached=news_id).order_by("-comments_post_date").values()


@login_required(login_url="/auth/login/")
def reply_send(request, news_id, comment_id):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    news_instance = News.objects.get(id=news_id)
    args = {
        "username": user_instance,
    }
    args.update(csrf(request))
    if request.POST:
        form = NewsCommentsRepliesForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment_attached = NewsComments.objects.get(id=comment_id)
            reply.news_attached = news_instance
            reply.reply_author = user_instance
            form.save()
    return HttpResponseRedirect("/news/%s/%s/" % (news_instance.news_category_id, news_id), args)


def replies_load(request, news_id):
    return NewsCommentsReplies.objects.filter(news_attached=news_id).order_by("reply_post_date").values()


@login_required(login_url="/auth/login/")
def add_like_news(request, news_id):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    if UserLikesNews.objects.filter(user_id=user_instance.id).filter(news_id=news_id).exists():
        user_like_instance = UserLikesNews.objects.filter(user_id=user_instance.id).get(news_id=news_id)
        user_like_instance.dislike = False
        user_like_instance.like = True
        user_like_instance.save()
    else:
        instance = News.objects.get(id=news_id)
        instance.news_likes += 1
        instance.save()
        UserLikesNews.objects.create(
            like=True,
            dislike=False,
            news_id=news_id,
            user_id=user_instance.id
        )
    return HttpResponse()


@login_required(login_url="/auth/login/")
def add_dislike_news(request, news_id):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    if UserLikesNews.objects.filter(user_id=user_instance.id).filter(news_id=news_id).exists():
        user_dislike_instance = UserLikesNews.objects.filter(user_id=user_instance.id).get(news_id=news_id)
        user_dislike_instance.dislike = True
        user_dislike_instance.like = False
        user_dislike_instance.save()
    else:
        instance = News.objects.get(id=news_id)
        instance.news_likes += 1
        instance.save()
        UserLikesNews.objects.create(
            like=False,
            dislike=True,
            news_id=news_id,
            user_id=user_instance.id
        )
    return HttpResponse()


def check_like_amount(request, news_id):
    return HttpResponse(json.dumps({"likes": UserLikesNews.objects.filter(news_id=news_id).filter(like=True).count()}),
                        content_type="application/json")


def check_dislike_amount(request, news_id):
    return HttpResponse(json.dumps({"dislikes": UserLikesNews.objects.filter(news_id=news_id).filter(dislike=True).count()}),
                        content_type="application/json")


#def delete_comment(request, comment_id):
#    args = {}
#    args.update(csrf(request))
#    news_instance = News.objects.get(id=NewsComments.objects.get(id=int(comment_id)).news_attached_id)
#    if User.objects.get(username=auth.get_user(request).username).is_staff:
#        instance = NewsComments.objects.get(id=int(comment_id))
#        instance.delete()
#    else:
#        pass
#    return HttpResponseRedirect("/news/%s/%s/" % (news_instance.news_category_id, news_instance.id), args)


#def delete_reply(request, reply_id):
#    args = {}
#    args.update(csrf(request))
#    news_instance = News.objects.get(id=NewsCommentsReplies.objects.get(id=int(reply_id)).news_attached_id)
#    if User.objects.get(username=auth.get_user(request).username).is_staff:
#        instance = NewsCommentsReplies.objects.get(id=int(reply_id))
#        instance.delete()
#    else:
#        pass
#    return HttpResponseRedirect("/news/%s/%s/" % (news_instance.news_category_id, news_instance.id), args)


#def shared_news_link(request, news_id):
#    news = News.objects.get(id=news_id)
#    shared_link = "http://127.0.0.1:8000/ext/trans/{0}/{1}/".format(news.news_category_id, news.id)
#    return shared_link


#def external_transition(request, cat_id, news_id):
#    news_instance = NewsWatches.objects.get(news_id=news_id)
#    news_instance.external_transition += 1
#    news_instance.save()
#    return HttpResponseRedirect("/news/%s/%s/" % (cat_id, news_id))


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





    portal_news_instance = RssNews.objects.filter(portal_name_id=int(pid))
    count_news = portal_news_instance.count() # amount of news on this portal

    list_of_news = portal_news_instance.order_by("-date_posted").values('id')

    for i in range(count_news):
        user_rss_instance = UserRssNewsReading.objects.get(user_id=user.id, rss_news_id=list_of_news[i]['id'])
        user_rss_instance.delete()

    # return render_to_response("user_news.html", args, context_instance=RequestContext(request))
    return HttpResponseRedirect("/news/usernews/")





def save_rss_news(request, rss_id):
    user = User.objects.get(username=auth.get_user(request).username)
    if not RssSaveNews.objects.filter(user_id=user.id).filter(rss_id=rss_id).exists():
        RssSaveNews.objects.create(
            user_id=user.id,
            rss_id=rss_id
        )
    else:
        pass
    return HttpResponse()


def forget_rss_news(request, rss_id):
    instance = RssSaveNews.objects.get(id=rss_id)
    instance.delete()
    # instance.save()
    return HttpResponse()


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
        "email": "support@insydia.com",
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


def render_current_portal_news(request, portal, template="user_news.html", page_template="current_portal_rss_news.html", extra_context=None):
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


def render_manager_portal(request):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    args = {
        "username": user_instance,

        "user_rss_portals": get_user_rss_portals(request, user_id=user_instance.id),
        "left_bar": False,
        "here_private": True,
    }
    args.update(csrf(request))

    return render_to_response("manage_portals.html", args)


def get_all_rss_portals(request):
    return RssPortals.objects.all().values()


def render_browser_portals(request, template="browse_portals.html", browse_template="browse_template.html", extra_context=None):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    args = {
        "username": user_instance,
        "browse_template": browse_template,
        "rss_portals": get_all_rss_portals(request),
        "user_rss_portals": get_user_rss_portals(request, user_id=user_instance.id),
        "left_bar": False,
        "here_private": True,

        "rss_tech": RssPortals.objects.filter(category=1).filter(
            id__in=get_user_unselceted_portals(request, user_id=user_instance.id).values_list("portal_id")
        ).order_by("-follows")[:4],
        "rss_ent": RssPortals.objects.filter(category=2).order_by("-follows")[:4],
        "rss_auto": RssPortals.objects.filter(category=3).order_by("-follows")[:4],
        "rss_space": RssPortals.objects.filter(category=4).order_by("-follows")[:4],
        "rss_bio": RssPortals.objects.filter(category=5).order_by("-follows")[:4],
    }
    args.update(csrf(request))

    if request.is_ajax():
        template = browse_template

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
    user_rss_instance = UserRssPortals.objects.get(portal_id=pid, user_id=user.id)
    if user_rss_instance.check == False:
        user_rss_instance.check = True
        user_rss_instance.save()
        rss_portal_instance = RssPortals.objects.get(id=int(pid))
        rss_portal_instance.follows += 1
        rss_portal_instance.save()
        data = {
            'data': RssPortals.objects.get(id=pid).get_json(),
            'exists': False,
            'string': """<li id="left-bar-portal-{portal_id}">
<a><span class="cprs" onclick="showCurrentPortalNews({portal_verbose});">{portal_name}</span>
<span class="count"></span></a></li>""",
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

