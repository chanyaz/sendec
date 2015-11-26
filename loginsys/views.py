from django.contrib import auth
from django.shortcuts import render, redirect, render_to_response, HttpResponseRedirect
from django.http import request
from django.template.context_processors import csrf

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.core.mail import send_mail

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
    return redirect('/auth/login/')


def register(request):
    from userprofile.models import UserSettings
    from .models import UserProfile

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
                # User Profile
                UserProfile.objects.create(
                    user_id=User.objects.get(username=auth.get_user(request).username).id,
                    confirmation_code=''.join(choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
                )


                user_email = request.POST["registration-email"]


                from django.conf import settings

                mail_subject = "Confirm your account on Severy, %s" % new_user_form.cleaned_data['username']
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
                send_mail(mail_subject, mail_message, settings.EMAIL_HOST_USER, [mail_to], fail_silently=False)






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