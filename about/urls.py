"""indavant URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.views.generic.base import RedirectView


# API MODELS
from news.models import News


from django.conf.urls import handler404
handler404 = 'news.views.page_not_found'


admin.autodiscover()
from rest_framework import routers
# from api.views import NewsViewSet


router = routers.DefaultRouter()
# router.register(r'news', NewsViewSet)


#import debug_toolbar

urlpatterns = patterns('',
    url(r'^advertisement/', 'about.views.render_adertisement_page'),
    url(r'^career/', 'about.views.render_career_page'),
    url(r'hello/', 'about.views.hello'),
    url(r'^telegram/', 'about.views.render_telegram_page'),
    url(r'^$', 'about.views.render_about_page'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
