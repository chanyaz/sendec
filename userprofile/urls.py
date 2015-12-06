from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'm/(?P<username>\w+)/', 'userprofile.views.render_moderator_profile_page'),
    url(r'^change/', 'userprofile.views.change_profile_data'),
    url(r"^photo_upload/", "userprofile.views.change_profile_photo"),
    url(r'^add_portals', 'userprofile.views.addition_portals_show'),
    url(r'^sce=(?P<user_id>\w+)', 'userprofile.views.send_confirm_email'),
    url(r'^$', 'userprofile.views.render_user_profile_page'),
]
