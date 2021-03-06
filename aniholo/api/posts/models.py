from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    raw_content = models.TextField()
    content_type = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=100)
    author = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    comments = models.IntegerField(default=0)
    date_posted = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    status = models.SmallIntegerField(default=0)  # 0 - default, 1 - edited, 2 - deleted

    class Meta:
        db_table = 'posts'

class Tag(models.Model):
    post = models.ManyToManyField(Post)
    tag_value = models.CharField(max_length=32, unique=True)

    class Meta:
        db_table = 'tags'

class Comment(MPTTModel):
    comment_id = models.AutoField(primary_key=True)
    author = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    raw_content = models.TextField()
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True)
    date_posted = models.DateTimeField(auto_now_add=True)

    class MPTTMeta:
        order_by_insertion = ['-score']
    
    class Meta:
        db_table = 'comments'


class Vote(models.Model):
    vote_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    vote_type = models.PositiveSmallIntegerField()
    vote_value = models.SmallIntegerField(default=0)
    object_id = models.IntegerField()

    class Meta:
        db_table = 'votes'
