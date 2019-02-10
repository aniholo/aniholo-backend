"""Define URL patterns for forums"""

from django.urls import path
from django.conf.urls import url

from . import views, serializers

app_name = 'tokenauthenticator'

urlpatterns = [
    path('token/', views.login_request, name='token_obtain_pair'),
    path('token/refresh/', views.refresh_request, name='token_refresh'),
    path('register/', views.register, name='register_user'),
    path('token/test/', views.test_token, name="test_token"),
    path('posts/create', views.create_post, name="create_post"),
]