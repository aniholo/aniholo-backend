from django.db import models

# Create your models here.

class User(models.Model):
	user_id = models.CharField(primary_key=True, max_length=50)
	username = models.CharField(unique=True, max_length=50)
	password = models.CharField(max_length=100, null=False)
	email = models.TextField(null=False)
	date_joined = models.IntegerField()
	last_login = models.IntegerField()
	secret = models.CharField(max_length=32, null=False)
	user_ip_address = models.CharField(max_length=15, blank=True, null=True)

	class Meta:
		app_label = 'authentification'
		managed = False
		db_table = 'users'