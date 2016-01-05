from django.contrib import auth
from django.contrib.auth import logout
from django.shortcuts import redirect, render_to_response, HttpResponseRedirect, HttpResponse
from django.template.context_processors import csrf
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from userprofile.models import UserSettings, UserRssPortals, User
from news.models import NewsPortal, NewsCategory, RssPortals
from .forms import UserCreationFormNew, UserAuthenticationForm
from .models import UserProfile
import uuid
import datetime
import json
import string
from random import choice, randint

from django import forms

SESSION_LIFE_TIME = 86400
SESSION_LIFE_TIME_REMEMBERED = 31536000


def login(request):
    args = {}
    args.update(csrf(request))
    if request.COOKIES.get("announce"):
        args["hide"] = False
    else:
        args["hide"] = True
    args["beta_announce"] = """<h5>Currently version is only for <i>beta testing</i>. We have hidden/disabled some functions and blocks.
<br>Beta test continues <b>till 21.12.15 17:00 GMT(UTC) +0300</b>
<br>If you found any problems or just want to tell us something else, you can <a href="/about/contacts/">write</a> to us
<br>We hope that next version(the last pre-release) will have all functions and design solutions which we build.</h5>
"""
    args["form"] = UserAuthenticationForm(request.POST)

    if auth.get_user(request).is_authenticated():
        return redirect("/")
    else:
        if request.POST and ("pause" not in request.session):
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                if "remember-true" in request.POST:
                    request.session.set_expiry(SESSION_LIFE_TIME_REMEMBERED)
                    request.session["pause"] = True

                else:
                    request.session.set_expiry(SESSION_LIFE_TIME)
                    request.session["pause"] = True
                return redirect('/')
            else:
                args['login_error'] = 'User not found. Please try again.'
                return render_to_response('login.html', args)
        else:
            args["img-num"] = randint(1, 4)
            args["background_url"] = "/static/static/img/login/{file_num}.jpg".format(file_num=randint(1, 7))
            return render_to_response('login.html', args)


@login_required(login_url='/auth/login/')
def user_logout(request):
    logout(request)
    return redirect('/')


def register(request):
    if auth.get_user(request).is_authenticated():
        return redirect("/")
    else:
        args = {}
        args.update(csrf(request))

        if request.COOKIES.get("announce"):
            args["hide"] = False
        else:
            args["hide"] = True
        args["beta_announce"] = """<h5>Currently version is only for <i>beta testing</i>. We have hidden/disabled some functions and blocks.
<br>Beta test continues <b>till 21.12.15 17:00 GMT(UTC) +0300</b>
<br>If you found any problems or just want to tell us something else, you can <a href="/about/contacts/">write</a> to us
<br>We hope that next version(the last pre-release) will have all functions and design solutions which we build.</h5>
"""

        args['form'] = UserCreationFormNew()
        if request.POST:
            new_user_form = UserCreationFormNew(request.POST)
            user_name = request.POST['username']
            if not check_username(request, username=user_name) == False:
                if new_user_form.is_valid():
                    new_user_form.save()
                new_user = auth.authenticate(username=user_name,
                                             password=request.POST['password1'])
                auth.login(request, new_user)
                # User settings
                UserSettings.objects.create(
                    user_id=User.objects.get(username=auth.get_user(request).username).id,
                )
                user_email = request.POST["email"]
                user_phone = "+0-000-000-00-00"
                #    request.POST["phone"]

                UserProfile.objects.create(
                    user_id=User.objects.get(username=auth.get_user(request).username).id,
                    confirmation_code=''.join(choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _
                                              in range(33)),
                    user_cell_number=user_phone,
                    uuid=set_uuid(User.objects.get(username=auth.get_user(request).username).id)
                )
                list_portals = RssPortals.objects.all().values()
                [UserRssPortals.objects.create(
                    user_id=User.objects.get(username=auth.get_user(request).username).id,
                    portal_id=int(list_portals[i]["id"]),
                    check=False
                ) for i in range(len(list_portals))]

                mail_subject = "Confirm your account on Insydia, %s" % user_name
                user_instance = User.objects.get(username=user_name)
                text_content = 'This is an important message.'
                htmly = render_to_string("confirm.html",
                                         {'username': user_instance.username,
                                          'email': user_email,
                                          'ucid': user_instance.profile.confirmation_code,
                                          'uuid': user_instance.profile.uuid})
                html_content = htmly
                mail_from = "insydia@yandex.ru"
                mail_to = user_email
                msg = EmailMultiAlternatives(mail_subject, text_content, mail_from, [mail_to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                instance = User.objects.get(username=auth.get_user(request).username)
                instance.is_active = False
                instance.email = user_email
                instance.save()
                return redirect('/')
        args["img-num"] = randint(1, 4)
        args["background_url"] = "/static/static/img/login/{file_num}.jpg".format(file_num=randint(1, 7))
        return render_to_response('register.html', args)


@login_required(login_url="/auth/login/")
def render_user_preferences_categories_page(request):
    if User.objects.get(username=auth.get_user(request).username).is_active:
        return HttpResponseRedirect("/")
    else:
        args = {
            "username": auth.get_user(request).username,
            "categories": get_categories_names(request),
        }
        args.update(csrf(request))

        if request.COOKIES.get("announce"):
            args["hide"] = False
        else:
            args["hide"] = True
        args["beta_announce"] = """<h5>Currently version is only for <i>beta testing(coursework)</i>. We have hidden/disabled some functions and blocks.
Beta test continues <b>till 21.12.15 17:00 GMT(UTC) +0300</b>
<br>If you found any problems or just want to tell us something else, you can <a href="/about/contacts/">write</a> to us
<br>We hope that next version will have localisation and mobile app at least for Android OS.</h5>
"""
        return render_to_response("user_preferences_categories.html", args)


@login_required(login_url="/auth/login/")
def render_user_preferences_portal_page(request):
    if User.objects.get(username=auth.get_user(request).username).is_active:
        return HttpResponseRedirect("/")
    else:
        args = {
            "username": auth.get_user(request).username,
            "portals": get_portals_names(request),
            }
        args.update(csrf(request))

        if request.COOKIES.get("announce"):
            args["hide"] = False
        else:
            args["hide"] = True
        args["beta_announce"] = """<h5>Currently version is only for <i>beta testing(coursework)</i>. We have hidden/disabled some functions and blocks.
Beta test continues <b>till 21.12.15 17:00 GMT(UTC) +0300</b>
<br>If you found any problems or just want to tell us something else, you can <a href="/about/contacts/">write</a> to us
<br>We hope that next version will have localisation and mobile app at least for Android OS.</h5>
"""
        return render_to_response("user_preferences_portals.html", args)


@login_required(login_url="/auth/login/")
def skip_preferences(request):
    instance = User.objects.get(username=auth.get_user(request).username)
    instance.is_active = True
    instance.save()
    return HttpResponseRedirect("/")


def get_portals_names(request):
    return NewsPortal.objects.all()


def get_categories_names(request):
    return NewsCategory.objects.all()


def pref_cat_save(request):
    args = {}
    args.update(csrf(request))

    settings_instance = UserSettings.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id)
    if request.POST:
        categories_list = request.POST.getlist("categories[]")
        for i in categories_list:
            if i not in settings_instance.portals_to_show:
                settings_instance.categories_to_show += "%s," % i
                settings_instance.save()
    return HttpResponseRedirect("/auth/preferences=portals")


def pref_portals_save(request):
    portals_settings = UserSettings.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id)
    if request.POST:
        portals_list = request.POST.getlist("portals[]")
        for i in portals_list:
            if i not in portals_settings.portals_to_show:
                portals_settings.portals_to_show += "%s," % i
                portals_settings.save()
    user_instance = User.objects.get(username=auth.get_user(request).username)
    user_instance.is_active = True
    user_instance.save()
    return HttpResponseRedirect("/")


def confirm_email(request, confirm_code, user_uuid):
    user_take = UserProfile.objects.get(uuid=user_uuid.replace('-', ''))
    user_instance = User.objects.get(id=user_take.user_id)
    if confirm_code == user_instance.profile.confirmation_code:
        user_instance.is_active = True
        user_instance.save()
    return HttpResponseRedirect('/')


#   ################################## SMS PIN #########################################

def send_message_via_sms(request, verify_code, phone_number):
    from twilio.rest import TwilioRestClient
    account_sid = "AC23d3af9ee2f38d74d4217e1ddb7b4c1c"
    auth_token = "6037a6a6474cf31ff68cf0b13146da45"
    client = TwilioRestClient(account_sid, auth_token)
    text = ", thank you for registration. Your verification code: %s" % verify_code
    client.messages.create(to=phone_number, from_="+12166001832", body=text,)


def set_uuid(user_id):
    user_instance = User.objects.get(id=user_id)
    return uuid.uuid3(uuid.NAMESPACE_DNS, "%s %s" % (user_instance.username, datetime.datetime.now()))


def check_username(request, username):
    if User.objects.filter(username=username).exists():
        return HttpResponse(json.dumps({"data": True}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"data": False}), content_type="application/json")


def render_help_login(request):
    args = {}
    args.update(csrf(request))

    return render_to_response("cant_login.html", args)