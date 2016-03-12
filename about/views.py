from django.shortcuts import render
from django.contrib import auth
from django.template.context_processors import csrf
from django.shortcuts import render_to_response, RequestContext, HttpResponse
from news.views import get_news_for_footer as nf
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import json


def render_about_page(request):
    args = {
        "title": "Contacts |",
        "left_bar": True,
    }
    args.update(csrf(request))
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = nf(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    response = render_to_response("about.html", args, context_instance=RequestContext(request))
    response.status_code = 200
    return response


def render_adertisement_page(request):
    args = {
        "title": "Advertisement | ",
        "left_bar": True,
    }
    args.update(csrf(request))
    if auth.get_user(request).username:
        args["username"] = User.objects.get(username=auth.get_user(request).username)
        args["search_private"] = True
    args["footer_news"] = nf(request)[:3]
    if "eng" in request.COOKIES.get('lang'):
        args['lang'] = 'eng'
    elif "rus" in request.COOKIES.get('lang'):
        args['lang'] = 'rus'
    elif "ch" in request.COOKIES.get('lang'):
        args['lang'] = 'ch'
    response = render_to_response("advertisers.html", args, context_instance=RequestContext(request))
    response.status_code = 200
    return response


def render_career_page(request):
    response=render_to_response("hire.html", context_instance=RequestContext(request))
    response.status_code=200
    return response


def render_telegram_page(request):
    response = render_to_response("telegram_guide.html", context_instance=RequestContext(request))
    response.status_code = 200
    return response


def hello(request):
    if request.POST:
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        mail_from = settings.DEFAULT_FROM_EMAIL
        mail_to = email
        mail_subject = "Insydia report."
        text_content = """Hello, {name}!
We recieved your message. Thanks you a lot.

If you have any questions, write their to <a href="support@insydia.com">support@insydia.com</a>

Yours faithfully,
Insydia Team.
""".format(name=name)
        html_content = """Hello, {name}!
We recieved your message. Thanks you a lot.

If you have any questions, write their to <a href="support@insydia.com">support@insydia.com</a>

Yours faithfully,
Insydia Team.
""".format(name=name)
        msg = EmailMultiAlternatives(mail_subject, text_content, mail_from, [mail_to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()





        mail_from = settings.DEFAULT_FROM_EMAIL
        mail_to_isydia = "support@insydia.com"
        mail_subject = "Insydia report."
        text_content = """{name} sent message to us.

<blockquote>{message}</blockquote>

name: {name}
email: {email}

""".format(name=name,email=email,message=message)
        html_content = """Hello, {name}!
We recieved your message. Thanks you a lot.

If you have any questions, write their to <a href="support@insydia.com">support@insydia.com</a>
""".format(name=name)
        msg = EmailMultiAlternatives(mail_subject, text_content, mail_from, [mail_to_isydia])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return HttpResponse(json.dumps({"data": "sent"}), content_type="application/json")


def send_resume(request):
    args = {}
    args.update(csrf(request))
    if request.POST:
        name = request.POST['name']
        email = request.POST['email']
        tel = request.POST['tel']
        text = request.POST['text']

        mail_subject = "[CAREER] Request a Career"
        mail_to = "hr@insydia.com"
        mail_from = settings.DEFAULT_FROM_EMAIL
        text_content = """User want to be a teammate"""
        html_content = """User want to be a teammate of Insydia.<br>

name: {name}<br>
email: {email}<br>
tel: {tel}<br>
<blockquote>
        {text}
</blockquote>
""".format(text=text, name=name, email=email, tel=tel)

        msg = EmailMultiAlternatives(mail_subject, text_content, mail_from, [mail_to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return HttpResponse(json.dumps({'data': True}), content_type="application/json")
