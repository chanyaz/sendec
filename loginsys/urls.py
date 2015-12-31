
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^cant_login/$', 'loginsys.views.render_help_login'),
    url(r'^login/$', 'loginsys.views.login'),
    url(r'^logout/$', 'loginsys.views.user_logout'),
    url(r'^ps/$', 'loginsys.views.pref_portals_save'),
    url(r'^cs/$', 'loginsys.views.pref_cat_save'),
    url(r'^preferences=categories$', "loginsys.views.render_user_preferences_categories_page"),
    url(r'^preferences=portals$', "loginsys.views.render_user_preferences_portal_page"),
    url(r'^skip-preferences/$', "loginsys.views.skip_preferences"),
    url(r'^register/cu=(?P<username>\w+)$', 'loginsys.views.check_username'),
    url(r'^register/$', 'loginsys.views.register'),
    url(r'^ucid=(?P<confirm_code>\w+)&uuid=(?P<user_uuid>[^/]+)/$', 'loginsys.views.confirm_email'),#&iid=(?P<email_hash>\w+)/', )
]
