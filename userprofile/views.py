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
        "test": get_portals_to_add(request)[0],
        "test_2": get_added_portals_name(request),
    }
    args.update(csrf(request))

    return render_to_response("settings.html", args)


def get_portal_names(request):
    from news.models import NewsPortal
    from userprofile.models import UserSettings
    news_list = list(NewsPortal.objects.get(id=int(cur_id)) for cur_id in get_portals_to_add(request)[0])
    return news_list#NewsPortal.objects.all()


def get_portals_to_add(request):
    from userprofile.models import UserSettings
    from news.models import News, NewsPortal
    user_setting_instance = UserSettings.objects.get(user_id=User.objects.get(username=auth.get_user(request).username).id).portals_to_show.split(",")
    list_of_portals_to_choose_by_user = NewsPortal.objects.all().values("id")
    new_user_list = []
    for i in list_of_portals_to_choose_by_user:
        if str(i["id"]) not in user_setting_instance:
            new_user_list.append(i["id"])
    return new_user_list, user_setting_instance

@login_required(login_url="/auth/login/")
def get_added_portals_name(request):
    from news.models import NewsPortal
    return [NewsPortal.objects.get(id=int(cur_id)) for cur_id in get_portals_to_add(request)[1][:-1]]


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
            if i not in settings_instance.portals_to_show:
                settings_instance.portals_to_show += "%s," % i
                settings_instance.save()

    return HttpResponseRedirect("/profile/settings/", args)