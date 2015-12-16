from django.shortcuts import render
from django.shortcuts import render_to_response, render, HttpResponseRedirect, RequestContext, HttpResponse, Http404
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
        "user_articles": 100,#get_user_articles_amount(User.objects.get(username=auth.get_user(request).username).id),
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
    args["beta_announce"] = """<h5>Currently version is only for <i>beta testing(coursework)</i>. We have hidden/disabled some functions and blocks.
Beta test continues <b>till 21.12.15 17:00 GMT(UTC) +0300</b>
<br>If you found any problems or just want to tell us something else, you can <a href="/about/contacts/">write</a> to us.\
<br>We hope that next version will have localisation and mobile app at least for Android OS.</h5>
"""

    if not UserProfile.objects.filter(user_id=User.objects.get(username=auth.get_user(request).username).id).exists():
        UserProfile.objects.create(
            user_id=User.objects.get(username=auth.get_user(request).username).id,
            user_photo="",
            user_cell_number=""
        )

    args["special_text"] = "To get special information you can enter key-word here and we will try to find and provide " \
                           "you with this information."

    return render_to_response("profile.html", args)


def render_moderator_profile_page(request, username):
    if User.objects.filter(username=username).exists():
        if User.objects.get(username=username).is_staff:

            from news.models import News
            user_moderator = User.objects.get(username=username),
            user = User.objects.get(username=auth.get_user(request).username),
            args = {
                "username": user,
                "moderator": user_moderator,
                "articles": News.objects.filter(news_author_id=1).values(),
            }
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
            return render_to_response("moderator_profile.html", args)
        else:
            raise Http404()
    else:
        raise Http404()


def get_user_articles(request, **kwargs):
    from loginsys.models import UserProfile
    return UserProfile.objects.get(user_id=User.objects.get(username=kwargs["looking_username"]).id).written_articles


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
    from .models import UserRssPortals, RssPortals
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
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings

    user_instance = User.objects.get(id=user_id)

    mail_subject = "Confirm your account on <service-name>, %s" % user_instance.username
    mail_message = """%s,
Last step of registration.
Please, confirm your account by clicking button below this text.
<button>Confirm now</button>

Or you can do it by use this link: <a href=''>%sc/ucid=%s&uid=%s</a>""" % \
                   (user_instance.username,
                    settings.MAIN_URL,
                    user_instance.profile.confirmation_code,
                    user_instance.profile.uuid)

    mail_from = "saqel@yandex.ru"
    mail_to = user_instance.email#User.objects.get(username=new_user_form.cleaned_data['username']).email
    #send_mail(mail_subject, mail_message, settings.EMAIL_HOST_USER, [mail_to], fail_silently=Fals
    text_content = 'This is an important message.'
    html_content = """<div id="wrapper" style="background-color: rgba(28, 28, 28, 0.17); width: 50%; margin-left: auto; margin-right: auto;">
        <div class="row" style=" width: 90%; margin-left: auto; margin-right: auto;">
            <table style="width: 600px">
                <tr>
                    <td>
                        <div class="" style="float: right">INSYDIA</div>
                    </td>
                </tr>
            </table>
            <table style="border:1px solid #dddddd;
                   background-color:#ffffff;"
                   width="600" cellpadding="0" border="0" cellspacing="0">
                <tbody>
                    <tr>
                        <td colspan="2" style="padding:30px 30px 0 30px;color:#444444;font-size:14px;line-height:1.5em;" align="left" valign="top">
                            <div style="font-size:14px;line-height:1.6em;color:#444444;">
                                Hi&nbsp;%s,
                                <p>
                                    Please confirm &nbsp;
                                    <a href="">
                                        %s
                                    </a>
                                    <span>
                                        .&nbsp;Thank&nbsp;you!
                                    </span>
                                </p>
                                <p style="text-align:center;">
                                    <a href="http://127.0.0.1:8004/c/ucid=%s&uuid=%s/" class="">
                                        <span style="font-size:16px;min-width:200px;background-color:#19ab58;line-height:42px;display:inline-block;color:white;border-radius:4px;text-align:center;margin-top:10px;padding:0 8px;">
                                            Confirm&nbsp;your&nbsp;e-mail&nbsp;»
                                        </span>
                                    </a>
                                </p>
                                <p>
                                    Cheers,
                                    <br>
                                    Your&nbsp;Insydia&nbsp;Team
                                    <br><br>
                                </p>
                                <p>

                                </p>
                                <div style="font-size:12px;color:#808080;">
                                    If&nbsp;you&nbsp;did&nbsp;not&nbsp;sign&nbsp;up&nbsp;or&nbsp;request&nbsp;for&nbsp;
                                    email&nbsp;confirmation,&nbsp;please&nbsp;ignore&nbsp;this&nbsp;email.
                                </div>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
            <table width="600px">
                <tr>
                    <td style="padding:5% 5% 0 5%; color:#444444; font-size:14px; line-height:1.5em; text-align: center;">
                        <div class="">
                            You&nbsp;are&nbsp;receiving&nbsp;this&nbsp;email&nbsp;because&nbsp;%s&nbsp;is&nbsp;registered&nbsp;on&nbsp;Insydia.
                            <br>Please&nbsp;do&nbsp;not&nbsp;reply&nbsp;directly&nbsp;to&nbsp;this&nbsp;email.&nbsp;If&nbsp;you&nbsp;have&nbsp;any&nbsp;questions&nbsp;or&nbsp;feedback,&nbsp;please&nbsp;visit&nbsp;our&nbsp;contact&nbsp;page.
                            <br>Copyright&nbsp;&#169;&nbsp;2015&nbsp;Insydia,&nbsp;|&nbsp;St.&nbsp;Petersburg,&nbsp;Russia
                        </div>
                    </td>
                </tr>
            </table>
        </div>
    </div>""" % \
                           (user_instance.username,
                            user_instance.email,
                            settings.MAIN_URL,
                            user_instance.profile.confirmation_code,
                            user_instance.profile.uuid,
                            user_instance.email)

    msg = EmailMultiAlternatives(mail_subject, text_content, mail_from, [mail_to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return HttpResponse()


def get_user_articles_amount(user_id):
    from news.models import News
    return News.objects.filter(news_author_id=user_id).count()