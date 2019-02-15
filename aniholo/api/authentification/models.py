from django.db import models

# Create your models here.

class User(models.Model):
	user_id = models.CharField(primary_key=True, max_length=16)
	username = models.CharField(max_length=16, unique=True)
	password = models.CharField(max_length=100)
	email = models.EmailField(max_length=254)
	date_joined = models.DateField(auto_now_add=True)
	last_login = models.DateTimeField(auto_now=True)
	secret = models.CharField(max_length=32)
	user_ipv4 = models.GenericIPAddressField(protocol='IPv4')
	user_perms = models.TextField(default="user")

	class Meta:
		db_table = 'users'