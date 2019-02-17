from django.urls import path
from django.conf.urls import url

from . import views, serializers

app_name = 'api.authentication'

urlpatterns = [
    path('create', views.create_comment, name='comment_create'), # create comment

]