"""Define URL patterns for forums"""

from django.urls import path
from django.conf.urls import url

from . import views, serializers

app_name = 'api.posts'

urlpatterns = [
    path('create', views.create_post, name='post_create'),  # create a post
    path('list', views.list_posts, name='post_list'),  # list posts for specific params
    path('get', views.get_post, name='post_get'),  # get data of a single post
    path('vote', views.vote, name='object_vote'),  # vote on an object
    path('comments', views.list_comment, name='comments_list'),  # list all comments
]