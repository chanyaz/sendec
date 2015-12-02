from django.shortcuts import render
from django.shortcuts import render_to_response, render, HttpResponseRedirect, RequestContext, HttpResponse
from django.template.context_processors import csrf
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


from loginsys.models import UserProfile


@login_required(login_url="/auth/login/")
def render_user_profile_page(request):
    args = {
        "username": User.objects.get(username=auth.get_user(request).username),
        "title": "| Profile",
        "user_profile_page": True,
        "user_articles": 100#get_user_articles_amount(User.objects.get(username=auth.get_user(request).username).id),
    }
    args.update(csrf(request))

    if not UserProfile.objects.filter(user_id=User.objects.get(username=auth.get_user(request).username).id).exists():
        UserProfile.objects.create(
            user_id=User.objects.get(username=auth.get_user(request).username).id,
            user_photo="",
            user_cell_number=""
        )

    return render_to_response("profile.html", args)


def get_user_articles(request, **kwargs):
    from loginsys.models import UserProfile
    return UserProfile.objects.get(user_id=User.objects.get(username=kwargs["looking_username"]).id).written_articles


@login_required(login_url="/auth/login/")
def render_settings(request):

    from news.models import RssNews, RssPortals

    args = {
        "username": User.objects.get(username=auth.get_user(request).username),
        "title": "| Settings",
        #"portals": get_portal_names(request),
        #"choosen_portals": get_currently_shown_portals(request),
        "test": get_portals_to_add(request),
        "test_2": get_added_portals_name(request),
        "categories": get_categories_names(request),
        "companies": get_companies(request),

        "hui": RssPortals.objects.all(),


    }
    args.update(csrf(request))

    return render_to_response("settings.html", args)


def get_companies(request):
    from news.models import Companies
    return Companies.objects.all().values("name")

def get_categories_names(request):
    from news.models import NewsCategory
    return NewsCategory.objects.all()

def get_portal_names(request):
    from news.models import NewsPortal
    from userprofile.models import UserSettings
    news_list = list(NewsPortal.objects.get(id=int(cur_id)) for cur_id in get_portals_to_add(request))
    return news_list#NewsPortal.objects.all()


def get_portals_to_add(request):
    from userprofile.models import UserSettings, UserRssPortals

    current_user = User.objects.get(username=auth.get_user(request).username)
    return UserRssPortals.objects.filter(user_id=current_user.id).filter(check=False).values("portal_id")

@login_required(login_url="/auth/login/")
def get_added_portals_name(request):
    from news.models import NewsPortal
    from userprofile.models import UserRssPortals
    current_user = User.objects.get(username=auth.get_user(request).username)
    return UserRssPortals.objects.filter(user_id=current_user.id).filter(check=True).values("portal_id")
    #return [NewsPortal.objects.get(id=int(cur_id)) for cur_id in get_portals_to_add(request)[1][:-1]]


def get_currently_shown_portals(request):
    from news.models import NewsPortal
    from userprofile.models import UserSettings
    portals_id = UserSettings.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id).portals_to_show.split(",")
    return portals_id


@login_required(login_url="/auth/login/")
def change_profile_data(request):
    from loginsys.models import UserProfile
    from .models import UserProfile
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
    from loginsys.models import UserProfile
    args = {}
    args.update(csrf(request))
    instance = User.objects.get(username=auth.get_user(request).username).profile
    if request.POST:
        instance.user_photo = request.FILES["username_photo"]
        instance.save()
    return HttpResponseRedirect("/profile/", args)


@login_required(login_url="/auth/login/")
def addition_portals_show(request):
    from news.models import NewsPortal
    from .models import UserSettings, UserRssPortals
    args = {}
    args.update(csrf(request))

    settings_instance = UserSettings.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id)


    if request.GET:
        portals_list = request.GET.getlist("source-to-show")
        for i in portals_list:

            rss_instance = UserRssPortals.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id,
                                                      portal_id=int(i))
            rss_instance.check = True
            rss_instance.save()

            #if i not in settings_instance.portals_to_show:
             #   settings_instance.portals_to_show += "%s," % i
              #  settings_instance.save()

        categories_list = request.GET.getlist("categories[]")
        for i in categories_list:
            if i not in settings_instance.categories_to_show.split(",")[:-1]:
                settings_instance.categories_to_show += "%s," % i
                settings_instance.save()

        for j in settings_instance.categories_to_show.split(",")[:-1]:
            if j not in categories_list:
                settings_instance.categories_to_show = settings_instance.categories_to_show.replace("%s," % j, "")
                settings_instance.save()

    return HttpResponseRedirect("/profile/settings/", args)


def send_confirm_email(request, user_id):
    from django.core.mail import EmailMultiAlternatives

    user_instance = User.objects.get(id=user_id)

    mail_subject = "Confirm your account on <service-name>, %s" % user_instance.username
    mail_message = """%s,
Last step of registration.
Please, confirm your account by clicking button below this text.
<button>Confirm now</button>

Or you can do it by use this link: <a href=''>http://127.0.0.1:8000/c/ucid=%s&uid=%s</a>""" % \
                   (user_instance.username,
                    user_instance.profile.confirmation_code,
                    user_instance.id)

    mail_from = "saqel@yandex.ru"
    mail_to = user_instance.email#User.objects.get(username=new_user_form.cleaned_data['username']).email
    #send_mail(mail_subject, mail_message, settings.EMAIL_HOST_USER, [mail_to], fail_silently=Fals
    text_content = 'This is an important message.'
    html_content = """%s,
\nThank you for registration at <service-name>
\n
\nTo confirm your account, you have to press this button.
\n<button style='margin-left: 30%%; width: 150px; height: 50px; background-color: #5bc0de; color: white;'
onclick="location.href='http://127.0.0.1:8000/c/ucid=%s&uid=%s';">Confirm&nbsp;now</button>
\n
\nOr you can do it via clicking url: <a href="http://127.0.0.1:8000/c/ucid=%s&uid=%s">http://127.0.0.1:8000/c/ucid=%s&uid=%s</a>""" % \
                   (user_instance.username,
                    user_instance.profile.confirmation_code,
                    user_instance.id,
                    user_instance.profile.confirmation_code,
                    user_instance.id,
                    user_instance.profile.confirmation_code,
                    user_instance.id)

    msg = EmailMultiAlternatives(mail_subject, text_content, mail_from, [mail_to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return HttpResponse()


def get_user_articles_amount(user_id):
    from news.models import News
    return News.objects.filter(news_author_id=user_id).count()