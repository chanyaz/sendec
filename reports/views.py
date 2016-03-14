from django.shortcuts import render
from django.http import HttpResponse
from django.core.context_processors import csrf
import json
from django.core.mail import send_mail
from .models import UserReports
from django.contrib.auth.models import User
from django.contrib import auth
from django.conf import settings


def user_report_of_not_exist_rss(request):
    args = {}
    args.update(csrf(request))
    if request.POST:
        user_instance = User.objects.get(username=auth.get_user(request).username)
        UserReports.objects.create(
            user_id=user_instance.id,
            email_new=request.POST['email'],
            rss=True,
            portal_link=request.POST['portal_link'],
        )

        user_to = user_instance.email
        user_from = settings.DEFAULT_FROM_EMAIL
        user_subject = "Insydia thanks for your report."
        user_text = """We have recieved a report of problems with portal({portal}).


        Thanks for report,
        Your Insydia Team
        """.format(portal=request.POST['portal_link'])
        send_mail(user_subject, user_text, user_from, [user_to])

        return HttpResponse(json.dumps({"message": "sent"}), content_type="application/json")