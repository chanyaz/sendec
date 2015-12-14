from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^$', 'notify.views.render_notify_page'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
