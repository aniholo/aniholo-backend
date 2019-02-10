from django.db import models

# Create your models here.

class Account(models.Model):
	user_id = models.AutoField(primary_key=True)
	username = models.CharField(unique=True, max_length=50)
	password = models.CharField(max_length=50)
	email = models.CharField(unique=True, max_length=355)
	created_on = models.DateTimeField()
	last_login = models.DateTimeField(blank=True, null=True)

	class Meta:
		app_label = 'account_stuff'
		managed = False
		db_table = 'account'

class Posts(models.Model):
    post_id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=150)
    title = models.CharField(max_length=1000)
    upvotes = models.CharField(max_length=1000)
    downvotes = models.CharField(max_length=1000)
    date_posted = models.DateTimeField()
    image_link = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'posts'
        app_label = 'post_stuff'