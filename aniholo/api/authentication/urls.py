"""Define URL patterns for forums"""

from django.urls import path
from django.conf.urls import url

from . import views, serializers

app_name = 'api.authentication'

urlpatterns = [
    path('login', views.login_request, name='token_obtain'),
    path('refresh', views.refresh_request, name='token_refresh'),
    path('register', views.register, name='register_user'),
    path('reset', views.reset_tokens, name='token_reset'),
]