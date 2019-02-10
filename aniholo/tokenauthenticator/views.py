from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class GetData(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'You have a valid access token!'}
        return Response(content)