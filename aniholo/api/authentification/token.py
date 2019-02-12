from api.authentification import models
from aniholo import settings

import jwt
import time

secret_key = settings.SECRET_KEY

def isValidToken(token):  # check if a given token is valid
	try:
		payload = jwt.decode(token, secret_key)
	except:
		return False

	if ("expiration_time" in payload):
		received_expire_time = payload.get("expiration_time")
		if int(time.time()) < received_expire_time:
			record = models.User.objects.get(user_id=payload.get("user_id"))
			return payload.get("user_secret") == record.secret
	return False

def encode(content):  # encode data
	return jwt.encode(content, secret_key)

def decode(content):  # encode data
	return jwt.decode(content, secret_key)