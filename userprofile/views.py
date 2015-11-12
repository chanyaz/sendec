from django.shortcuts import render
from django.shortcuts import render_to_response, render
from django.template.context_processors import csrf
from django.contrib import auth


def render_user_profile_page(request):
    args = {
        "username": auth.get_user(request).username,
        "title": "| Profile",
        "user_profile_page": True,
    }
    args.update(csrf(request))

    return render_to_response("profile.html", args)