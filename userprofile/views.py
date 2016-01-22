from django.shortcuts import render_to_response, HttpResponseRedirect, HttpResponse, Http404, RequestContext, loader
from django.template.context_processors import csrf
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required, user_passes_test
from django.template.loader import render_to_string
from news.models import News, Companies, NewsCategory, NewsPortal
from userprofile.models import UserProfile, UserSettings, UserRssPortals, RssPortals, ModeratorSpecialFields
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
import datetime

from django.core import signing
from django.contrib.sites.models import Site, RequestSite


@login_required(login_url="/auth/login/")
def render_user_profile_page(request):

    from password_reset.forms import PasswordRecoveryForm

    user_instance = User.objects.get(username=auth.get_user(request).username)

    args = {
        "username": user_instance,
        "title": "Profile | ",
        "user_profile_page": True,
        "user_articles": get_user_articles_amount(user_instance.id),
        "test": get_portals_to_add(request),
        "test_2": get_added_portals_name(request),
        "categories": get_categories_names(request),
        "companies": get_companies(request),
        "form": PasswordRecoveryForm,
    }

    if user_instance.is_staff:
        args["god"] = get_god_data(request, user_instance.username)


    args.update(csrf(request))

    if not UserProfile.objects.filter(user_id=user_instance.id).exists():
        UserProfile.objects.create(
            user_id=user_instance.id,
            user_photo="",
            user_cell_number=""
        )
    args["search_private"] = True
    args["special_text"] = "To get special information you can enter key-word here and we will try to find and provide " \
                           "you with this information."
    args["footer_news"] = get_news_for_footer(request)[:3]
    return render_to_response("profile.html", args)


def get_news_for_footer(request):
    return News.objects.order_by("-news_post_date").defer("news_dislikes").defer("news_likes").defer("news_post_text_english").defer("news_post_text_chinese").defer("news_post_text_russian").defer("news_author").defer("news_portal_name")


def get_site(request):
        if Site._meta.installed:
            return Site.objects.get_current()
        else:
            return RequestSite(request)

def send_notification(request):

    instance_user = User.objects.get(username=auth.get_user(request).username)
    email_template_name = 'password_reset/recovery_email.txt'
    email_subject_template_name = 'password_reset/recovery_email_subject.txt'

    context = {
        'site': get_site(request),
        'user': instance_user,
        'username': instance_user.username,
        'token': signing.dumps(instance_user.pk, salt="password_recovery"),
        'secure': request.is_secure(),
    }
    body = loader.render_to_string(email_template_name,
                                   context).strip()
    subject = loader.render_to_string(email_subject_template_name,
                                      context).strip()
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
              [instance_user.email])
    return HttpResponseRedirect("/profile/")

def render_moderator_profile_page(request, username, template="moderator_profile.html", page_template="moderator_news.html", extra_context=None):
    user_instance = User.objects.get(username=auth.get_user(request).username)
    if User.objects.filter(username=username).exists():
        if User.objects.get(username=username).is_staff:
            user_moderator = User.objects.get(username=username)
            articles = News.objects.filter(news_author_id=user_moderator.id).defer("news_post_text_chinese").defer("news_post_text_russian").defer("news_likes").defer("news_dislikes").values()
            args = {
                "username": user_instance,
                "moderator": user_moderator,
                "articles": articles,
                "articles_count": articles.count(),
                "page_template": page_template,
            }
            args.update(csrf(request))
            args["god"] = get_god_data(request, user_moderator.username)
            if request.is_ajax():
                template = page_template

            args["footer_news"] = get_news_for_footer(request)[:3]
            return render_to_response(template, args, context_instance=RequestContext(request))
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
    try:
        if "userlogin" in request.POST:
            return render_to_response("403.html", {"username": instance})
    except:
        send_access_report(request)
        return render_to_response("403.html", {"username": instance})
    if request.POST:
        instance.first_name = request.POST["first_name"]
        instance.last_name = request.POST["last_name"]
        instance.email = request.POST["email"]
        instance.profile.user_cell_number = request.POST["cell"]
        instance.profile.save()
        instance.save()

        if instance.is_staff:
            save_special_fields(request, instance.username, {
                "facebook": request.POST["facebook"],
                "twitter": request.POST["twitter"],
                "linkedin": request.POST["linkedin"],
                "vk": request.POST["vk"],
                "personal_email": request.POST["personal_email"]
            })

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


def check_admin_or_not(user):
    return user.is_staff


# @staff_member_required(view_func=user_passes_test, login_url="/admin/")
@user_passes_test(test_func=check_admin_or_not, login_url="/admin/")
def save_special_fields(request, god, fields):
    god_user_instance = User.objects.get(username=god)
    if ModeratorSpecialFields.objects.filter(user_id=god_user_instance.id).exists():
        god_instance = ModeratorSpecialFields.objects.get(user_id=god_user_instance.id)
        god_instance.facebook = fields["facebook"]
        god_instance.twitter = fields["twitter"]
        god_instance.linkedin = fields["linkedin"]
        god_instance.vk = fields["vk"]
        god_instance.personal_email = fields["personal_email"]
        god_instance.save()
    else:
        ModeratorSpecialFields.objects.create(
            user_id=god_user_instance.id,
            facebook=fields["facebook"],
            twitter=fields["twitter"],
            linkedin=fields["linkedin"],
            vk=fields["vk"],
            personal_email=fields["personal_email"]
        )

    return HttpResponseRedirect("/profile/")


def get_god_data(request, god):
    return ModeratorSpecialFields.objects.get(user_id=User.objects.get(username=god).id)


def send_access_report(request):
    instance = User.objects.get(username=auth.get_user(request).username)
    mail_subject = "[HACK] Someone wants to change login."
    mail_message = "User {username}(id:{id}) at {time} wants to change username(login) through change html code of" \
                   "username field.".format({"username": instance.username,
                                             "id": instance.id,
                                             "time": datetime.datetime.now()})
    html_content = "User {username}(id:{id}) at {time} wants to change username(login) through change html code of" \
                   "<i>username</i> field.".format({"username": instance.username,
                                                    "id": instance.id,
                                                    "time": datetime.datetime.now()})
    mail_from = mail_to = "support@insydia.com"
    msg = EmailMultiAlternatives(mail_subject, mail_message, mail_from, [mail_to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return HttpResponse()



def send_request_message(request, username, keyword):
    mail_subject = "[RSS REQUEST] Someone wants to change login."
    mail_message = """User %s(id: %s) at %s request to add new RSS portal(keyword: "%s") via profile form.\n\n
User e-mail: %s""" % (username.username, username.id, datetime.datetime.now(), keyword, username.email)
    html_content = """User %s(id: %s) at %s request to add new RSS portal(keyword: <i>%s</i>) via profile form.
User e-mail: %s""" % \
                   (username.username, username.id, datetime.datetime.now(),  keyword, username.email)
    mail_from = "noreply@insydia.com"
    msg = EmailMultiAlternatives(mail_subject, mail_message, mail_from, ["support@insydia.com", "eprivalov@insydia.com"])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return HttpResponse()


def user_request_rss_portal(request):
    instance = User.objects.get(username=auth.get_user(request).username)
    args = {
        "username": instance,
    }
    args.update(csrf(request))
    if request.POST:
        key_word = request.POST["keyword"]
        send_request_message(request, username=instance, keyword=key_word)
    return HttpResponseRedirect("/profile/")
