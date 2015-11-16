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
    }
    args.update(csrf(request))

    return render_to_response("profile.html", args)


@login_required(login_url="/auth/login/")
def render_settings(request):
    args = {
        "username": User.objects.get(username=auth.get_user(request).username),
        "title": "| Settings",
        "portals": get_portal_names(request),
        "choosen_portals": get_currently_shown_portals(request),
    }
    args.update(csrf(request))

    return render_to_response("settings.html", args)


def get_portal_names(request):
    from news.models import NewsPortal
    return NewsPortal.objects.all()


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
    from .models import UserSettings
    args = {}
    args.update(csrf(request))

    settings_instance = UserSettings.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id)

    if request.GET:
        portals_list = request.GET.getlist("source-to-show")
        for i in portals_list:
            settings_instance.portals_to_show += "%s," % i
            settings_instance.save()

    return HttpResponse()