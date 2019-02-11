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

# class Posts(models.Model):
#     post_id = models.AutoField(primary_key=True)
#     author = models.CharField(max_length=150)
#     title = models.CharField(max_length=1000)
#     upvotes = models.CharField(max_length=1000)
#     downvotes = models.CharField(max_length=1000)
#     date_posted = models.DateTimeField()
#     image_link = models.CharField(max_length=250, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'posts'
#         app_label = 'post_stuff'

class Posts(models.Model):
    post_id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=150, blank=True, null=True)
    title = models.CharField(max_length=1000, blank=True, null=True)
    upvotes = models.CharField(max_length=1000, blank=True, null=True)
    downvotes = models.CharField(max_length=1000, blank=True, null=True)
    date_posted = models.DateTimeField(blank=True, null=True)
    image_link = models.CharField(max_length=250, blank=True, null=True)
    is_nsfw = models.BooleanField(blank=True, null=True)
    is_spoiler = models.BooleanField(blank=True, null=True)
    source_material = models.CharField(max_length=1000, blank=True, null=True)
    required_tag = models.CharField(max_length=30)
    other_tags = models.CharField(max_length=10000, blank=True, null=True)
    is_announcement = models.BooleanField(blank=True, null=True)
    post_text = models.CharField(max_length=10000, blank=True, null=True)
    post_type = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'posts'
        app_label = 'post_stuff'

class Tags(models.Model):
    tag_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tags'
        app_label = 'tag_stuff'

class PostTagPivot(models.Model):
    post_id = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    tag_id = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'post_tag_pivot'
        app_label = 'post_and_tag_stuff'