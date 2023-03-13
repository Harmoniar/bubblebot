from django.urls import path, include, reverse
from django.views.static import serve
from django.conf import settings
from admin import urls as admin_urls
from robot import urls as robot_urls


MEDIA_URL = "{}<path:path>".format(settings.MEDIA_URL.lstrip('/'))
STATIC_URL = "{}<path:path>".format(settings.STATIC_URL.lstrip('/'))

urlpatterns = [
    path('', admin_urls.views.empty_url),
    path('admin/', include(admin_urls.urlpatterns)),
    path('robot/', include(robot_urls.urlpatterns)),
    path(MEDIA_URL, serve, {'document_root': settings.MEDIA_ROOT}, name='admin_media'),
    path(STATIC_URL, serve, {'document_root': settings.STATIC_ROOT}, name='admin_static'),
]
