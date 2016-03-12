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

from rss.views import \
    RssChannelLatestEnglish, \
    RssChannelLatestChinese, \
    RssChannelLatestRussian, \
    RssChannelLatestWeekEnglish, \
    RssChannelLatestWeekChinese, \
    RssChannelLatestWeekRussian, \
    RssChannelTechnologyEnglish, \
    RssChannelTechnologyChinese, \
    RssChannelTechnologyRussian, \
    RssChannelEntertainmentEnglish, \
    RssChannelEntertainmentChinese, \
    RssChannelEntertainmentRussian, \
    RssChannelAutoEnglish, \
    RssChannelAutoChinese, \
    RssChannelAutoRussian, \
    RssChannelSpaceEnglish, \
    RssChannelSpaceChinese, \
    RssChannelSpaceRussian, \
    RssChannelBioEnglish, \
    RssChannelBioChinese, \
    RssChannelBioRussian, \
    RssChannelCompany, \
    RssChannelTechnologyWeekEnglish, RssChannelTechnologyWeekChinese, RssChannelTechnologyWeekRussian, \
    RssChannelEntertainmentWeekEnglish, \
    RssChannelEntertainmentWeekChinese, \
    RssChannelEntertainmentWeekRussian, \
    RssChannelAutoWeekEnglish, \
    RssChannelAutoWeekRussian, \
    RssChannelAutoWeekChinese, \
    RssChannelSpaceWeekEnglish, \
    RssChannelSpaceWeekChinese, \
    RssChannelSpaceWeekRussian, \
    RssChannelBioWeekEnglish, \
    RssChannelBioWeekChinese, \
    RssChannelBioWeekRussian
from rss.views import RenderRSSPage

urlpatterns = patterns('',
    url(r'^gcr/', 'rss.views.get_current_company_rss'),
    url(r'^news&channel=company&name=(?P<company_name>\w+)$', RssChannelCompany()),

    # Technology WEEK for all langs
    url(r'^news&channel=technology&range=week&lang=eng', RssChannelTechnologyWeekEnglish()),
    url(r'^news&channel=technology&range=week&lang=ch', RssChannelTechnologyWeekChinese()),
    url(r'^news&channel=technology&range=week&lang=rus', RssChannelTechnologyWeekRussian()),

    # Technology TODAY for all langs
    url(r'^news&channel=technology&lang=eng', RssChannelTechnologyEnglish()),
    url(r'^news&channel=technology&lang=ch', RssChannelTechnologyChinese()),
    url(r'^news&channel=technology&lang=rus', RssChannelTechnologyRussian()),


    url(r'^news&channel=entertainment&range=week&lang=eng', RssChannelEntertainmentWeekEnglish()),
    url(r'^news&channel=entertainment&range=week&lang=ch', RssChannelEntertainmentWeekChinese()),
    url(r'^news&channel=entertainment&range=week&lang=rus', RssChannelEntertainmentWeekRussian()),

    url(r'^news&channel=entertainment&lang=eng', RssChannelEntertainmentEnglish()),
    url(r'^news&channel=entertainment&lang=ch', RssChannelEntertainmentChinese()),
    url(r'^news&channel=entertainment&lang=rus', RssChannelEntertainmentRussian()),


    url(r'^news&channel=auto&range=week&lang=eng', RssChannelAutoWeekEnglish()),
    url(r'^news&channel=auto&range=week&lang=ch', RssChannelAutoWeekChinese()),
    url(r'^news&channel=auto&range=week&lang=rus', RssChannelAutoWeekRussian()),

    url(r'^news&channel=auto&lang=eng', RssChannelAutoEnglish()),
    url(r'^news&channel=auto&lang=ch', RssChannelAutoChinese()),
    url(r'^news&channel=auto&lang=rus', RssChannelAutoRussian()),


    url(r'^news&channel=space&range=week&lang=eng', RssChannelSpaceWeekEnglish()),
    url(r'^news&channel=space&range=week&lang=ch', RssChannelSpaceWeekChinese()),
    url(r'^news&channel=space&range=week&lang=rus', RssChannelSpaceWeekRussian()),

    url(r'^news&channel=space&lang=eng', RssChannelSpaceEnglish()),
    url(r'^news&channel=space&lang=ch', RssChannelSpaceChinese()),
    url(r'^news&channel=space&lang=rus', RssChannelSpaceRussian()),


    url(r'^news&channel=bio&range=week&lang=eng', RssChannelBioWeekEnglish()),
    url(r'^news&channel=bio&range=week&lang=ch', RssChannelBioWeekChinese()),
    url(r'^news&channel=bio&range=week&lang=rus', RssChannelBioWeekRussian()),

    url(r'^news&channel=bio&lang=eng', RssChannelBioEnglish()),
    url(r'^news&channel=bio&lang=ch', RssChannelBioChinese()),
    url(r'^news&channel=bio&lang=rus', RssChannelBioRussian()),


    url(r'^news&channel=latest&range=week&lang=eng', RssChannelLatestWeekEnglish()),
    url(r'^news&channel=latest&range=week&lang=ch', RssChannelLatestWeekChinese()),
    url(r'^news&channel=latest&range=week&lang=rus', RssChannelLatestWeekRussian()),

    url(r'^news&channel=latest&lang=eng', RssChannelLatestEnglish()),
    url(r'^news&channel=latest&lang=ch', RssChannelLatestChinese()),
    url(r'^news&channel=latest&lang=rus', RssChannelLatestRussian()),


    url(r'^', RenderRSSPage.as_view()),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)