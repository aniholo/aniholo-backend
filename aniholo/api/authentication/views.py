from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError
from rest_framework.decorators import api_view

from . import models, token
from aniholo import settings

from passlib.hash import argon2

import secrets
import time
import datetime
import ast

from django.utils import timezone


EXPIRATION_TIME = 600  # 10 mins
REFRESH_EXPIRATION_TIME = 86400  # 1 day

VALID_USER_PERMS = ['user', 'moderator', 'admin']

@csrf_exempt 
@api_view(['POST'])
def login_request(request):
	#TODO - Set server-side limits to refresh times

	if "user_id" not in request.POST or "password" not in request.POST:
		return Response({"status": "failed", "error": "must include both username and password"})
	
	user_id = request.POST.get("user_id")  # the id is used to log in, not the name (it's changeable)
	password = request.POST.get("password")

	access_expiration_time = int(request.POST.get('access_duration', EXPIRATION_TIME))  # default values
	refresh_expiration_time = int(request.POST.get('refresh_duration', REFRESH_EXPIRATION_TIME))

	try:
		record = models.User.objects.get(user_id=user_id)
	except models.User.DoesNotExist:
		return Response({"status": "failed", "error": "incorrect login details"})
	
	if (not argon2.verify(password, record.password)):
		return Response({"status": "failed", "error": "incorrect login details"})

	current_time = int(time.time())  # adding issual_time and expiration_time

	try:
		record.save()
	except:
		return Response({"status": "failed", "error": "internal server error"})

	json_user_id = record.user_id

	refresh_token_content = {
		"user_id": json_user_id,
		"issual_time": current_time,
		"user_secret": record.secret,
		"expiration_time" : current_time + refresh_expiration_time
	}
	refresh_token = token.encode(refresh_token_content)
	
	access_token_content = {
		"user_id": json_user_id,
		"issual_time": current_time,
		"user_secret": record.secret,
		"expiration_time" : current_time + access_expiration_time
	}
	access_token = token.encode(access_token_content)

	return Response({"status": "success", "refresh_token": refresh_token, "access_token": access_token})

@csrf_exempt 
@api_view(['POST'])
def refresh_request(request):  # refresh an access token via the refresh_token
	if "user_id" not in request.POST or "refresh_token" not in request.POST:
		return Response({"status": "failed", "error": "must include user id and refresh token"})
	
	user_id = request.POST.get('user_id')
	refresh_token = request.POST.get('refresh_token')

	if not token.isValidToken(refresh_token):
		return Response({"status": "failed", "error": "invalid token"})

	payload = token.decode(refresh_token)
	
	token_user_id = payload.get('user_id')

	if user_id != token_user_id:
		return Response({"status": "failed", "error": "user ids don't match"})

	access_expiration_time = int(request.POST.get('access_duration', EXPIRATION_TIME))  # default value

	current_time = int(time.time())  # adding issual_time and expire_time

	access_token_content = {
		"user_id": token_user_id,
		"issual_time": current_time,
		"user_secret": payload.get('user_secret'),
		"expiration_time" : current_time + access_expiration_time
	}
	access_token = token.encode(access_token_content)

	return Response({"status": "success", "access_token": access_token})


@csrf_exempt 
@api_view(['POST'])
def register(request):
	if "user_id" not in request.POST or "email" not in request.POST or "password" not in request.POST:
		return Response({"status": "failed", "error": "must include user id, email and password"})

	user_event = models.User(user_id=request.POST.get("user_id"), email=request.POST.get("email"),
							 password=argon2.using(rounds=10).hash(request.POST.get("password")),
							 username=request.POST.get("username", None), user_ipv4=request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0] if request.META.get('HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR'),
							 secret=secrets.token_hex(16))
	
	try:
		user_event.save(force_insert=True)
		return Response({'status': 'success'})
	except IntegrityError:
		return Response({"status": "failed", "error": "user already exists"})
	except:
		return Response({"status": "failed", "error": "internal server error"})

@csrf_exempt
@api_view(['POST'])
def reset_tokens(request):
	# this method will also invalidate the token used to call this method.
	# in the future, may have function return a new, valid token.

	if "access_token" not in request.POST or "user_id" not in request.POST:
		return Response({"status": "failed", "error": "must include user id and token"})

	if not token.isValidToken(request.POST.get("access_token")):
		return Response({"status": "failed", "error": "invalid token"})

	payload = token.decode(request.POST.get("access_token"))
	
	token_user_id = payload.get('user_id')

	if request.POST.get("user_id") != token_user_id:
		return Response({"status": "failed", "error": "user ids don't match"})

	try:
		record = models.User.objects.get(user_id=token_user_id)
	except models.User.DoesNotExist:
		# in case, some how the user is removed from database while still having a token
		# may not be necessary but just for caution.
		return Response({"status": "failed", "error": "user does not exist"})

	record.secret = secrets.token_hex(16)

	try:
		record.save()
	except:
		return Response({"status": "failed", "error": "internal server error"})

	return Response({"status": "success"})

@csrf_exempt
@api_view(['POST'])
def change_perms(request):
	# change the user permissions of a user
	# this can only be done by a user who has admin perms.
	
	if "access_token" not in request.POST or "user_id" not in request.POST or "new_role" not in request.POST:
		return Response({"status": "failed", "error": "must include user id, token, and new permission role"})

	if not token.isValidToken(request.POST.get("access_token")):
		return Response({"status": "failed", "error": "invalid token"})

	payload = token.decode(request.POST.get("access_token"))	
	token_user_id = payload.get('user_id')	

	try:
		requesting_user_record = models.User.objects.get(user_id=token_user_id)
	except models.User.DoesNotExist:
		# in case, some how the user is removed from database while still having a token
		# may not be necessary but just for caution.
		return Response({"status": "failed", "error": "user does not exist"})

	# check the user to be changed exists
	try:
		changing_user_record = models.User.objects.get(user_id=request.POST.get('user_id'))
	except models.User.DoesNotExist:
		return Response({"status": "failed", "error": "user does not exist"})

	# check that the user is indeed an admin
	if requesting_user_record.user_perms != "admin":
		return Response({"status": "failed", "error": "invalid authorization to change user role"})

	# check that the new role is a valid role.
	if request.POST.get('new_role').lower() not in VALID_USER_PERMS:
		return Response({"status": "failed", "error": "invalid user role provided"})

	changing_user_record.user_perms = request.POST.get('new_role').lower()

	try:
		changing_user_record.save()
	except:
		return Response({"status": "failed", "error": "internal server error"})

	return Response({"status": "success"})

@csrf_exempt
@api_view(['POST'])
def change_pass(request):
	if "access_token" not in request.POST or "new_password" not in request.POST or "old_password" not in request.POST:
		return Response({"status": "failed", "error": "must include token, new password, and old password"})

	if not token.isValidToken(request.POST.get("access_token")):
		return Response({"status": "failed", "error": "invalid token"})

	payload = token.decode(request.POST.get("access_token"))
	token_user_id = payload.get('user_id')

	old_password = request.POST.get('old_password')

	try:
		user = models.User.objects.get(user_id=token_user_id)
	except models.User.DoesNotExist:
		return Response({"status": "failed", "error": "user does not exist"})
	
	if (not argon2.verify(old_password, user.password)):
		return Response({"status": "failed", "error": "current password provided is incorrect"})

	user.password = argon2.using(rounds=10).hash(request.POST.get("new_password"))

	try:
		user.save()
	except:
		return Response({"status": "failed", "error": "internal server error"})

	return Response({"status": "success"})