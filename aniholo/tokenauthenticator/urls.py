"""Define URL patterns for forums"""

from django.urls import path
from django.conf.urls import url

from . import views, serializers

app_name = 'tokenauthenticator'

urlpatterns = [
    path('token/', serializers.MyTokenObtainView.as_view(), name='token_obtain_pair'),
    path('token/refresh', serializers.MyTokenRefreshView.as_view(), name='token_refresh'),
    path('test_access/', views.GetData.as_view()),
]