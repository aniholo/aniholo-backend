from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError
from django.db.models import Count
from django.utils.dateformat import format
from rest_framework.decorators import api_view
from api.authentication.models import User

from aniholo import settings
from api.authentication import token

@csrf_exempt
@api_view(['POST'])
def edit_profile(request):
	if "access_token" not in request.POST:
		return Response({"status": "failed", "error": "must include token"})

	if not token.isValidToken(request.POST.get("access_token")):
		return Response({"status": "failed", "error": "invalid token"})

	payload = token.decode(request.POST.get('access_token'))
	token_user_id = payload.get('user_id')

	user = User.objects.get(user_id=token_user_id)

	if "new_username" in request.POST:
		user.username = request.POST.get('new_username')

	if "new_email" in request.POST:
		user.email = request.POST.get('new_email')

	try:
		user.save()
	except:
		return Response({"status": "failed", "error": "internal server error"})

	return Response({"status": "success"})