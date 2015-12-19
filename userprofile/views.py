from django.shortcuts import render_to_response, HttpResponseRedirect, HttpResponse, Http404
from django.template.context_processors import csrf
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from news.models import News, Companies, NewsCategory, NewsPortal
from userprofile.models import UserProfile, UserSettings, UserRssPortals, RssPortals
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


@login_required(login_url="/auth/login/")
def render_user_profile_page(request):
    user_instance = User.objects.get(username=auth.get_user(request).username)

    args = {
        "username": user_instance,
        "title": "| Profile",
        "user_profile_page": True,
        "user_articles": get_user_articles_amount(user_instance.id),
        "test": get_portals_to_add(request),
        "test_2": get_added_portals_name(request),
        "categories": get_categories_names(request),
        "companies": get_companies(request),
    }
    args.update(csrf(request))

    if request.COOKIES.get("announce"):
        args["hide"] = False
    else:
        args["hide"] = True
    args["beta_announce"] = """<h5>Currently version is only for <i>beta testing</i>. We have hidden/disabled some functions and blocks.
<br>Beta test continues <b>till 21.12.15 17:00 GMT(UTC) +0300</b>
<br>If you found any problems or just want to tell us something else, you can <a href="/about/contacts/">write</a> to us.\
<br>We hope that next version(the last pre-release) will have all functions and design solutions which we build.</h5>
"""

    if not UserProfile.objects.filter(user_id=user_instance.id).exists():
        UserProfile.objects.create(
            user_id=user_instance.id,
            user_photo="",
            user_cell_number=""
        )

    args["special_text"] = "To get special information you can enter key-word here and we will try to find and provide " \
                           "you with this information."

    return render_to_response("profile.html", args)


def render_moderator_profile_page(request, username):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    if User.objects.filter(username=username).exists():
        if User.objects.get(username=username).is_staff:
            user_moderator = User.objects.get(username=username),
            args = {
                "username": user_instance,
                "moderator": user_moderator,
                "articles": News.objects.filter(news_author_id=1).values(),
            }
            args.update(csrf(request))

            if request.COOKIES.get("announce"):
                args["hide"] = False
            else:
                args["hide"] = True
            args["beta_announce"] = """<h5>Currently version is only for <i>beta testing</i>. We have hidden/disabled some functions and blocks.
<br>Beta test continues <b>till 21.12.15 17:00 GMT(UTC) +0300</b>
<br>If you found any problems or just want to tell us something else, you can <a href="/about/contacts/">write</a> to us.\
<br>We hope that next version(the last pre-release) will have all functions and design solutions which we build.</h5>
"""
            return render_to_response("moderator_profile.html", args)
        else:
            raise Http404()
    else:
        raise Http404()


def get_user_articles(request, **kwargs):
    return UserProfile.objects.get(user_id=User.objects.get(username=kwargs["looking_username"]).id).written_articles


def get_companies(request):
    return Companies.objects.all().values("name")


def get_categories_names(request):
    return NewsCategory.objects.all()


def get_portal_names(request):
    news_list = list(NewsPortal.objects.get(id=int(cur_id)) for cur_id in get_portals_to_add(request))
    return news_list


def get_portals_to_add(request):
    current_user = User.objects.get(username=auth.get_user(request).username)
    return UserRssPortals.objects.filter(user_id=current_user.id).filter(check=False).values("portal_id")


@login_required(login_url="/auth/login/")
def get_added_portals_name(request):
    current_user = User.objects.get(username=auth.get_user(request).username)
    return UserRssPortals.objects.filter(user_id=current_user.id).filter(check=True).values("portal_id")


def get_currently_shown_portals(request):
    portals_id = UserSettings.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id).portals_to_show.split(",")
    return portals_id


@login_required(login_url="/auth/login/")
def change_profile_data(request):
    args = {}
    args.update(csrf(request))
    instance = User.objects.get(username=auth.get_user(request).username)
    if request.POST:
        instance.first_name = request.POST["first_name"]
        instance.last_name = request.POST["last_name"]
        instance.email = request.POST["email"]
        instance.profile.user_cell_number = request.POST["cell"]
        instance.profile.save()
        instance.save()
    return HttpResponseRedirect("/profile/", args)


@login_required(login_url="/auth/login/")
def change_profile_photo(request):
    args = {}
    args.update(csrf(request))
    instance = User.objects.get(username=auth.get_user(request).username).profile
    if request.POST:
        instance.user_photo = request.FILES["username_photo"]
        instance.save()
    return HttpResponseRedirect("/profile/", args)


@login_required(login_url="/auth/login/")
def addition_portals_show(request):
    args = {}
    args.update(csrf(request))
    if request.GET:
        portals_list = request.GET.getlist("source-to-show")
        for i in portals_list:

            rss_instance = UserRssPortals.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id,
                                                      portal_id=int(i))
            rss_portal_instance = RssPortals.objects.get(id=int(i))

            rss_portal_instance.follows += 1
            rss_portal_instance.save()

            rss_instance.check = True
            rss_instance.save()
    return HttpResponseRedirect("/profile/", args)


def send_confirm_email(request, user_id):
    user_instance = User.objects.get(id=user_id)
    mail_subject = "Confirm your account on <service-name>, %s" % user_instance.username
    mail_message = """Hi, %s,
Please, confirm your e-mail.

Follow the link: <a href=''>%sc/ucid=%s&uid=%s</a>""" % \
                   (user_instance.username,
                    settings.MAIN_URL,
                    user_instance.profile.confirmation_code,
                    user_instance.profile.uuid)
    mail_from = "saqel@yandex.ru"
    mail_to = user_instance.email
    text_content = 'This is an important message.'
    htmly = render_to_string("confirm.html",
                             {'username': user_instance.username,
                              'email': user_instance.email,
                              'ucid': user_instance.profile.confirmation_code,
                              'uuid': user_instance.profile.uuid})
    html_content = htmly
    msg = EmailMultiAlternatives(mail_subject, text_content, mail_from, [mail_to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return HttpResponse()


def get_user_articles_amount(user_id):
    return News.objects.filter(news_author_id=user_id).count()