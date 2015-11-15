from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^change/', 'userprofile.views.change_profile_data'),
    url(r"^photo_upload/", "userprofile.views.change_profile_photo"),
    url(r"^settings/", "userprofile.views.render_settings"),
    url(r'^', 'userprofile.views.render_user_profile_page'),
]
