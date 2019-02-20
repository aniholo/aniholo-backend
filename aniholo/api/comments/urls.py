from django.urls import path
from django.conf.urls import url

from . import views, serializers

app_name = 'api.authentication'

urlpatterns = [
    path('create', views.create_comment, name='comment_create'), # create comment
    path('edit', views.edit_comment, name='comment_edit'),
    path('delete', views.delete_comment, name='comment_delete'),
    path('get', views.get_comment, name='comment_get'),

]