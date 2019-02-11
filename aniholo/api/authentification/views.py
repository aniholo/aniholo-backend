from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError
from rest_framework.decorators import api_view

from . import models
from aniholo import settings

from passlib.hash import argon2

import jwt

import time
import ast

EXPIRATION_TIME = 600  # 10 mins
REFRESH_EXPIRATION_TIME = 86400  # 1 day

def isValidToken(token):  # check if a given token is valid
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
def login_request(request):
	#TODO - Set server-side limits to refresh times

	if "user_id" not in request.POST or "password" not in request.POST:
		return Response({"status": "failed - must include both username and password"})
	
	user_id = request.POST.get("user_id")  # the id is used to log in, not the name (it's changeable)
	password = request.POST.get("password")

	access_expiration_time = int(request.POST.get('access_duration', EXPIRATION_TIME))  # default values
	refresh_expiration_time = int(request.POST.get('refresh_duration', REFRESH_EXPIRATION_TIME))

	try:
		record = models.User.objects.get(user_id=user_id)
	except models.User.DoesNotExist:
		return Response({"status": "failed - incorrect login details"})
	
	if (not argon2.verify(password, record.password)):
		return Response({"status": "failed - incorrect login details"})

	current_time = int(time.time())  # adding issual_time and expiration_time

	record.last_login = current_time

	try:
		record.save()
	except:
		return Response({"status": "failed - internal server error"})

	secret_key = settings.SECRET_KEY  #get server's secret key from settings.py
	json_user_id = record.user_id

	refresh_token_content = {
		"user_id": json_user_id,
		"issual_time": current_time,
		"expiration_time" : current_time + refresh_expiration_time
	}
	refresh_token = jwt.encode(refresh_token_content, secret_key)
	
	access_token_content = {
		"user_id": json_user_id,
		"issual_time": current_time,
		"expiration_time" : current_time + access_expiration_time
	}
	access_token = jwt.encode(access_token_content, secret_key)

	headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"}
	return Response({"status": "success", "refresh_token": refresh_token, "access_token": access_token}, headers=headers)

@csrf_exempt 
@api_view(['POST'])
def refresh_request(request):  # refresh an access token via the refresh_token
	if "user_id" not in request.POST or "refresh_token" not in request.POST:
		return Response({"status": "failed - must include user id and refresh token"})
	
	user_id = request.POST.get('user_id')
	refresh_token = request.POST.get('refresh_token')

	secret_key = settings.SECRET_KEY

	if not isValidToken(refresh_token):
		return Response({"access": "failed"})

	payload = jwt.decode(refresh_token, secret_key)
	
	token_user_id = payload.get('user_id')

	if user_id != token_user_id:
		return Response({"status": "failed - user ids don't match"})

	access_expiration_time = int(request.POST.get('access_duration', EXPIRATION_TIME))  # default value

	current_time = int(time.time())  # adding issual_time and expire_time

	access_token_content = {
		"user_id": token_user_id,
		"issual_time": current_time,
		"expiration_time" : current_time + access_expiration_time
	}
	access_token = jwt.encode(access_token_content, secret_key)

	return Response({"status": "success", "access_token": access_token})


@csrf_exempt 
@api_view(['POST'])
def register(request):
	if "user_id" not in request.POST or "email" not in request.POST or "password" not in request.POST:
		return Response({"status": "failed - must include user id, email and password"})

	user_event = models.User(user_id=request.POST.get("user_id"), email=request.POST.get("email"),
							 password=argon2.using(rounds=10).hash(request.POST.get("password")),
							 username=request.POST.get("username", None), date_joined=time.time())
	
	#try:
	user_event.save(force_insert=True)
	return Response({'status': 'success'})
	#except IntegrityError:
	#	return Response({"status": "failed - user already exists"})
	#except:
	#	return Response({"status": "failed - internal server error"})