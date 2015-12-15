from django.contrib import auth
from django.contrib.auth import logout
from django.shortcuts import render, redirect, render_to_response, HttpResponseRedirect
from django.http import request
from django.template.context_processors import csrf

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.core.mail import send_mail, EmailMultiAlternatives

import os
import datetime
from django.db.models import F
from django.http.request import HttpRequest
from django.contrib.auth.decorators import login_required


from .forms import UserCreationFormNew


SESSION_LIFE_TIME = 86400
SESSION_LIFE_TIME_REMEMBERED = 31536000


def login(request):
    args = {}
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
                args['login_error'] = 'User not found.'
                return render_to_response('index_new.html', args)
        else:
            return render_to_response('index_new.html', args)


#@login_required(login_url='/auth/login/')
def user_logout(request):
    logout(request)
    return redirect('/')


def register(request):
    from userprofile.models import UserSettings, UserRssPortals
    from .models import UserProfile
    import uuid

    from news.models import NewsPortal

    import string
    from random import choice

    if auth.get_user(request).is_authenticated():
        return redirect("/")
    else:
        args = {}
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

        args['form'] = UserCreationFormNew()
        if request.POST:
            new_user_form = UserCreationFormNew(request.POST)
            user_name = request.POST['username']
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
            user_phone = "+0-000-000-00-00"#request.POST["phone"]
            # User Profile creating
            UserProfile.objects.create(
                user_id=User.objects.get(username=auth.get_user(request).username).id,
                confirmation_code=''.join(choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33)),
                user_cell_number=user_phone,
                uuid=set_uuid(User.objects.get(username=auth.get_user(request).username).id)
            )
            #uuid_string = str(User.objects.get(username=new_user_form.cleaned_data['username']).profile.uuid).replace('-', '')
            uuid_string = User.objects.get(username=user_name).profile.uuid
            from news.models import RssNews, RssPortals
            list_portals = RssPortals.objects.all().values()
            [UserRssPortals.objects.create(
                user_id=User.objects.get(username=auth.get_user(request).username).id,
                portal_id=int(list_portals[i]["id"]),
                check=False
            ) for i in range(len(list_portals))]
            from django.conf import settings
            mail_subject = "Confirm your account on <service-name>, %s" % user_name
            mail_message = """%s,
Last step of registration.
Please, confirm your account by clicking button below this text.
<button>Confirm now</button>

Or you can do it by use this link: <a href=''>%sc/ucid=%s&uuid=%s/</a>""" % \
                           (user_name,
                            settings.MAIN_URL,
                            UserProfile.objects.get(user_id=User.objects.get(username=user_name).id).confirmation_code,
                            User.objects.get(username=user_name).profile.uuid)
            mail_from = "insydia@yandex.ru"
            mail_to = user_email#User.objects.get(username=new_user_form.cleaned_data['username']).email
            #send_mail(mail_subject, mail_message, settings.EMAIL_HOST_USER, [mail_to], fail_silently=False)


            text_content = 'This is an important message.'
            html_content = """%s,
\nThank you for registration at
\n
\nTo confirm your account, you have to press this button.
\n<button style='margin-left: 30%%; width: 150px; height: 50px; background-color: #5bc0de; color: white;'
onclick="location.href='%sc/ucid=%s&uuid=%s/';">Confirm&nbsp;now</button>
\n
\nOr you can do it via clicking url: <a href="%sc/ucid=%s&uuid=%s/">%sc/ucid=%s&uuid=%s</a>""" % \
                           (user_name,
                            settings.MAIN_URL,
                            UserProfile.objects.get(user_id=User.objects.get(username=user_name).id).confirmation_code,
                            uuid_string,
                            settings.MAIN_URL,
                            UserProfile.objects.get(user_id=User.objects.get(username=user_name).id).confirmation_code,
                            uuid_string,
                            settings.MAIN_URL,
                            UserProfile.objects.get(user_id=User.objects.get(username=user_name).id).confirmation_code,
                            uuid_string)
            msg = EmailMultiAlternatives(mail_subject, text_content, mail_from, [mail_to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            # Sending verification code via SMS.
            # send_message_via_sms(request,
            #                      verify_code=UserProfile.objects.get(user_id=User.objects.get(username=new_user_form.cleaned_data['username']).id).confirmation_code,
            #                      phone_number=user_phone)
            instance = User.objects.get(username=auth.get_user(request).username)
            instance.is_active = False
            instance.email = user_email
            instance.save()
            return redirect('/')
            #else:
            #    args['form'] = new_user_form
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
<br>If you found any problems or just want to tell us something else, you can <a href="/about/contacts/">write</a> to us.\
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
<br>If you found any problems or just want to tell us something else, you can <a href="/about/contacts/">write</a> to us.\
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
    from news.models import NewsPortal
    return NewsPortal.objects.all()


def get_categories_names(request):
    from news.models import NewsCategory
    return NewsCategory.objects.all()


def pref_cat_save(request):
    from userprofile.models import UserSettings
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
    from userprofile.models import UserSettings
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
    from loginsys.models import UserProfile
    user_take = UserProfile.objects.get(uuid=user_uuid.replace('-',''))
    user_instance = User.objects.get(id=user_take.user_id)
    if confirm_code == user_instance.profile.confirmation_code:
        user_instance.is_active = True
        user_instance.save()
    return HttpResponseRedirect('/')


import random
from django.core.cache import cache
from django.http.response import HttpResponse
from twilio.rest import TwilioRestClient


################################### SMS PIN #########################################

def send_message_via_sms(request, verify_code, phone_number):

    # Download the twilio-python library from http://twilio.com/docs/libraries
    from twilio.rest import TwilioRestClient

    # Find these values at https://twilio.com/user/account
    account_sid = "AC23d3af9ee2f38d74d4217e1ddb7b4c1c"
    auth_token = "6037a6a6474cf31ff68cf0b13146da45"
    client = TwilioRestClient(account_sid, auth_token)

    text = "Stanislav, thank you for registration. Your verification code: %s" % verify_code

    client.messages.create(to=phone_number, from_="+12166001832", body=text,)


def set_uuid(user_id):
    user_instance = User.objects.get(id=user_id)
    import uuid
    return uuid.uuid3(uuid.NAMESPACE_DNS, "%s %s" % (user_instance.username, datetime.datetime.now()))