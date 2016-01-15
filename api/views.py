from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from news.models import News
from news.serializer import NewsSerializer
from django.utils.html import strip_tags
from django.template.context_processors import csrf
from django.shortcuts import redirect, render_to_response, HttpResponseRedirect, HttpResponse

import jwt
import json


class SaltMixin(object):
    news_salt = "api_news_token"
    user_salt = "api_user_token"
    rss_salt = "api_rss_token"
    companies_salt = "api_companies_token"

    def __init__(self, model, *args, **kwargs):
        self.model = model
        if self.model == 'news':
            self.get_token(salt=self.news_salt, model=self.model)

    def get_token(self, model, salt=news_salt):
        return jwt.encode(payload={'salt': salt, 'model': model, 'mobile': True}, key='news', algorithm='HS256')


@api_view(['GET'])
def get_news_token(request, model):
    try:
        token = SaltMixin.get_token(request, model=model)
    except ValueError:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response({"token": token.decode()})


@api_view(['GET'])
def news_list(request, token, offset):
    if jwt.decode(token, key='news', algorithms=['HS256'])['salt'] == 'api_news_token':
    # print(token)
    # if jwt.encode(payload={'salt': 'api_news_token', 'model': 'news', 'mobile': True}, key='news', algorithm='HS256').decode() == token:
        try:
            if offset == "all":
                news = News.objects.all()
            else:
                news = News.objects.all()[:int(offset)]
        except News.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = NewsSerializer(news, many=True)
            return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def news_detail(request, token, news_id):
    if jwt.decode(token, key='news', algorithms=['HS256'])['salt'] == 'api_news_token':
        try:
            news = News.objects.get(id=int(news_id))
            news.news_post_text_english = strip_tags(news.news_post_text_english)
        except News.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            serializer = NewsSerializer(news)
            return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


def render_api_page(request):
    args = {}
    args.update(csrf(request))

    return render_to_response("api.html", args)
