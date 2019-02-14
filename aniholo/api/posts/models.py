from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    raw_content = models.TextField()
    content_type = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=100)
    author = models.ForeignKey('authentification.User', on_delete=models.CASCADE)
    comments = models.IntegerField(default=0)
    author_name = models.CharField(max_length=16)
    date_posted = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)

class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    tag_value = models.CharField(max_length=32)
    post = models.ForeignKey('Post', on_delete=models.CASECADE)

class Comment(MPTTModel):
    comment_id = models.AutoField(primary_key=True)
    author = models.ForeignKey('authentification.User', on_delete=models.CASCADE)
    author_name = models.CharField(max_length=16)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    raw_content = models.TextField()
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True)
    date_posted = models.DateTimeeFIeld(auto_now_add=True)

    class MPTTMeta:
        order_by_insertion = ['-score']

class Vote(models.Model):
    vote_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentification.User', on_delete=models.CASCADE)
    vote_type = models.PositiveSmallIntegerField()
    vote_value = models.SmallIntegerField()
    object_id = models.IntegerField()