import datetime

from django.utils.six import text_type

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class MyTokenObtainSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(TokenObtainPairSerializer, self).validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = text_type(refresh)
        if ('expiry_time' in self.initial_data):
            new_token = refresh.access_token
            new_token.set_exp(lifetime=datetime.timedelta(seconds=int(self.initial_data['expiry_time'])))
            data['access'] = text_type(new_token)
        else:
            data['access'] = text_type(refresh.access_token)
        return data


class MyTokenObtainView(TokenObtainPairView):
    serializer_class = MyTokenObtainSerializer


class MyTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        data = {'access': text_type(refresh.access_token)}

        refresh.set_jti()
        if ('expiry_time' in self.initial_data):
            new_token = refresh.access_token
            print(int(self.initial_data['expiry_time']))
            new_token.set_exp(lifetime=datetime.timedelta(seconds=int(self.initial_data['expiry_time'])))
            data = {'access': text_type(new_token)}
        else:
            refresh.access_token.set_exp(lifetime=datetime.timedelta(seconds=300))

        return data


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer