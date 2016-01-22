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

from rss.views import RssChannelLatest,RssChannelTechnology,RssChannelEntertainment,RssChannelAuto,RssChannelSpace,RssChannelBio,RssChannelCompany,\
    RssChannelLatestWeek, RssChannelTechnologyWeek, RssChannelEntertainmentWeek, RssChannelAutoWeek, RssChannelSpaceWeek,RssChannelBioWeek
from rss.views import RenderRSSPage

urlpatterns = patterns('',
    url(r'^gcr/', 'rss.views.get_current_company_rss'),
    url(r'^news&channel=company&name=(?P<company_name>\w+)$', RssChannelCompany()),
    url(r'^news&channel=technology&range=week', RssChannelTechnologyWeek()),
    url(r'^news&channel=technology', RssChannelTechnology()),
    url(r'^news&channel=entertainment&range=week', RssChannelEntertainmentWeek()),
    url(r'^news&channel=entertainment', RssChannelEntertainment()),
    url(r'^news&channel=auto&range=week', RssChannelAutoWeek()),
    url(r'^news&channel=auto', RssChannelAuto()),
    url(r'^news&channel=space&range=week', RssChannelSpaceWeek()),
    url(r'^news&channel=space', RssChannelSpace()),
    url(r'^news&channel=bio&range=week', RssChannelBioWeek()),
    url(r'^news&channel=bio', RssChannelBio()),
    url(r'^news&channel=latest&range=week', RssChannelLatestWeek()),
    url(r'^news&channel=latest', RssChannelLatest()),
    url(r'^', RenderRSSPage.as_view()),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)