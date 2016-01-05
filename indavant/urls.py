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

from django.conf.urls import handler404
handler404 = 'news.views.page_not_found'

urlpatterns = patterns('',
    url(r'^about/', include('news.urls')),
    url(r'^about', 'news.views.render_about_page'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('loginsys.urls')),
    url(r'^ext/', include("news.urls")),
    url(r'^favourite/', include('favourite.urls')),
    url(r'^news/', include('news.urls')),
    url(r'^news/', include('news.urls')),
    url(r'^news/', include('news.urls')),
    url(r'^notify/', include('notify.urls')),
    url(r'^profile/', include('userprofile.urls')),
    url(r'^search/', include('search.urls')),
    url(r'^pref/', include('loginsys.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^c/', include('loginsys.urls')),
    url(r'^en/', 'news.views.main_page_load'),
    url(r'^ru/', 'news.views.translate_russian'),
    url(r'^cn/', 'news.views.translate_chinese'),
    url(r'^$', 'news.views.global_redirect'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)