"""Define URL patterns for forums"""

from django.urls import path
from django.conf.urls import url

from . import views, serializers

app_name = 'api.posts'

urlpatterns = [
    path('create', views.create_post, name='post_create'),
]