from django.db import models

# Create your models here.

class User(models.Model):
	user_id = models.TextField(primary_key=True, max_length=50)
	username = models.CharField(unique=True, max_length=50)
	password = models.CharField(max_length=50)
	email = models.CharField(unique=True, max_length=355)
	date_joined = models.IntegerField()
	last_login = models.IntegerField()

	class Meta:
		app_label = 'user_data'
		managed = False
		db_table = 'users'