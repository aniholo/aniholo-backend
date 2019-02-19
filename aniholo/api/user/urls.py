"""Define URL patterns for forums"""

from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'api.user'

urlpatterns = [
    path('edit', views.edit_profile, name='user_edit'), 
]