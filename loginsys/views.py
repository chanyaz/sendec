from django.contrib import auth
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


SESSION_LIFE_TIME = 86400
SESSION_LIFE_TIME_REMEMBERED = 31536000


def login(request):
    args = {}
    args.update(csrf(request))

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
                return render_to_response('login.html', args)
        else:
            return render_to_response('login.html', args)


@login_required(login_url='/auth/login/')
def logout(request):
    auth.logout(request)
    return redirect('/')


def register(request):
    from userprofile.models import UserSettings, UserRssPortals
    from .models import UserProfile

    from news.models import NewsPortal

    import string
    from random import choice

    if auth.get_user(request).is_authenticated():
        return redirect("/")
    else:
        args = {}
        args.update(csrf(request))
        args['form'] = UserCreationForm()
        if request.POST:
            new_user_form = UserCreationForm(request.POST)
            if new_user_form.is_valid():
                new_user_form.save()
                new_user = auth.authenticate(username=new_user_form.cleaned_data['username'],
                                             password=new_user_form.clean_password2())
                auth.login(request, new_user)

                # User settings
                UserSettings.objects.create(
                    user_id=User.objects.get(username=auth.get_user(request).username).id,
                )

                user_email = request.POST["registration-email"]
                user_phone = request.POST["registration-phone"]


                # User Profile creating
                UserProfile.objects.create(
                    user_id=User.objects.get(username=auth.get_user(request).username).id,
                    confirmation_code=''.join(choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33)),
                    user_cell_number=user_phone
                )

                from news.models import RssNews, RssPortals

                list_portals = RssPortals.objects.all().values()
                [UserRssPortals.objects.create(
                    user_id=User.objects.get(username=auth.get_user(request).username).id,
                    portal_id=int(list_portals[i]["id"]),
                    check=False
                ) for i in range(len(list_portals))]

                from django.conf import settings


                mail_subject = "Confirm your account on <service-name>, %s" % new_user_form.cleaned_data['username']
                mail_message = """%s,
Last step of registration.
Please, confirm your account by clicking button below this text.
<button>Confirm now</button>

Or you can do it by use this link: <a href=''>http://127.0.0.1:8000/c/ucid=%s&uid=%s</a>""" % \
                               (new_user_form.cleaned_data['username'],
                                UserProfile.objects.get(user_id=User.objects.get(username=new_user_form.cleaned_data['username']).id).confirmation_code,
                                User.objects.get(username=new_user_form.cleaned_data['username']).id)
                mail_from = "saqel@yandex.ru"
                mail_to = user_email#User.objects.get(username=new_user_form.cleaned_data['username']).email
                #send_mail(mail_subject, mail_message, settings.EMAIL_HOST_USER, [mail_to], fail_silently=False)


                text_content = 'This is an important message.'
                html_content = """%s,
\nThank you for registration at <service-name>
\n
\nTo confirm your account, you have to press this button.
\n<button style='margin-left: 30%%; width: 150px; height: 50px; background-color: #5bc0de; color: white;'
onclick="location.href='http://127.0.0.1:8000/c/ucid=%s&uid=%s';">Confirm&nbsp;now</button>
\n
\nOr you can do it via clicking url: <a href="http://127.0.0.1:8000/c/ucid=%s&uid=%s">http://127.0.0.1:8000/c/ucid=%s&uid=%s</a>""" % \
                               (new_user_form.cleaned_data['username'],
                                UserProfile.objects.get(user_id=User.objects.get(username=new_user_form.cleaned_data['username']).id).confirmation_code,
                                User.objects.get(username=new_user_form.cleaned_data['username']).id,
                                UserProfile.objects.get(user_id=User.objects.get(username=new_user_form.cleaned_data['username']).id).confirmation_code,
                                User.objects.get(username=new_user_form.cleaned_data['username']).id,
                                UserProfile.objects.get(user_id=User.objects.get(username=new_user_form.cleaned_data['username']).id).confirmation_code,
                                User.objects.get(username=new_user_form.cleaned_data['username']).id)
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
            else:
                args['form'] = new_user_form
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


def confirm_email(request, confirm_code, user_id):
    user_instance = User.objects.get(id=user_id)
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


