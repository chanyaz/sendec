from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^', 'userprofile.views.render_user_profile_page'),
]
