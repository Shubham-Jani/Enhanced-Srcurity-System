from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, video_feed
from django.conf import settings
from django.conf.urls.static import static


routers = routers.DefaultRouter()
routers.register('users', UserViewSet)
urlpatterns = [
    path('', include(routers.urls)),
    path('test/', video_feed)
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
