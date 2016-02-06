from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from news.models import News
# from news.serializer import NewsSerializer
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
            return Response(serializer.data, content_type="application/json; charset=utf-8")
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def news_cat_list(request, token, cat_id, offset):
    if jwt.decode(token, key='news', algorithms=['HS256'])['salt'] == 'api_news_token':
    # print(token)
    # if jwt.encode(payload={'salt': 'api_news_token', 'model': 'news', 'mobile': True}, key='news', algorithm='HS256').decode() == token:
        try:
            if offset == "all":
                news = News.objects.filter(news_category_id=int(cat_id)).order_by("-news_post_date")
            else:
                news = News.objects.filter(news_category_id=int(cat_id)).order_by("-news_post_date")[:int(offset)]
        except News.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = NewsSerializer(news, many=True)
            return Response(serializer.data, content_type="application/json; charset=utf-8")
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def news_detail(request, token, news_id):
    if jwt.decode(token, key='news', algorithms=['HS256'])['salt'] == 'api_news_token':
        try:
            news = News.objects.get(id=int(news_id))
            news.news_post_text_english = strip_tags(news.news_post_text_english)
            news.news_post_test_russian = strip_tags(news.news_post_test_russian)
            news.news_post_text_chinese = strip_tags(news.news_post_text_chinese)
        except News.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            serializer = NewsSerializer(news)
            return Response(serializer.data, content_type="application/json; charset=utf-8")
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


def render_api_page(request):
    args = {}
    args.update(csrf(request))

    return render_to_response("rest_api.html", args)


################################################################################################
###############################################################################################
################################################################################################

from .serializers import UserSerializer,GroupSerializer,NewsSerializer
from rest_framework import permissions, viewsets
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope, TokenHasScope
from django.contrib.auth.models import User, Group
import django_filters
from rest_framework import filters
from rest_framework import generics


class NewsFilter(django_filters.FilterSet):
    class Meta:
        model = News
        fields = ['id', 'news_category', 'news_portal_name', 'news_company_owner', 'news_author']


class NewsViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticatedOrReadOnly]
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = NewsFilter

