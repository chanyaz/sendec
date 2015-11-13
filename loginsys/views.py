from django.contrib import auth
from django.shortcuts import render, redirect, render_to_response
from django.http import request
from django.template.context_processors import csrf

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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
                user_settings = UserSettings()

                UserProfile.objects.create(
                    user_id=User.objects.get(username=auth.get_user(request).username).id,
                )

                new_user_profile = auth.get_user(request)
                new_user_profile.birthday = "1900-01-01"
                new_user_profile.phone = "+1-234-567-89-90"
                new_user_profile.save()
                return redirect('/')
            else:
                args['form'] = new_user_form
        return render_to_response('register.html', args)
