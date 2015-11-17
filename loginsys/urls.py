
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^login/', 'loginsys.views.login'),
    url(r'^logout/', 'loginsys.views.logout'),
    url(r'^preferences/', "loginsys.views.render_user_preferences_page"),
    url(r'^register/', 'loginsys.views.register'),
]
