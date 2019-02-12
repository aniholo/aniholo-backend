from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError
from rest_framework.decorators import api_view

from . import models
from aniholo import settings

import jwt

import time
import ast

def isValidToken(token):
	secret_key = settings.SECRET_KEY

	payload = None

	try:
		payload = jwt.decode(token, secret_key)
	except (Exception):
		return False

	if ("expire_time" in payload):
		received_expire_time = payload.get("expire_time")
		return int(time.time()) < received_expire_time
	return True

@csrf_exempt 
@api_view(['POST'])
def create_post(request):
	if "token" not in request.POST or "title" not in request.POST or "content" not in request.POST or "content_type" not in request.POST:
		return Response({"status": "failed", "error": "must include token, title, content and content type"})

	if not isValidToken(request.POST.get("token")):
		return Response({"status": "failed", "error": "invalid token"})

	secret_key = settings.SECRET_KEY
	payload = jwt.decode(request.POST.get("token"), secret_key)

	user_id = payload.get("user_id")
	title = request.POST.get("title")
	content = request.POST.get("content")
	content_type = int(request.POST.get("content_type"))
	tags = str(request.POST.get("tags", "")).split(",")
	date_posted = time.time()

	post = models.Post(author=user_id, title=title,
						date_posted=date_posted, content=content,
						content_type=content_type)

	try:
		post.save(force_insert=True)

		for tag in tags:
			tag, _ = models.PostTag.objects.get_or_create(tag_value=tag)
			models.PostTagPivot.objects.create(post_id=post.post_id, tag_id=tag.tag_id)

		return Response({'status': 'success'})
	except:
		return Response({"status": "failed", "error": "internal server error"})