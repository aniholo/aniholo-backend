from django.db import models

# Create your models here.

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=50, null=False)
    title = models.TextField(null=False)
    content = models.TextField(null=False)
    content_type = models.SmallIntegerField(null=False)
    score = models.IntegerField(null=False, default=0)
    date_posted = models.IntegerField(null=False)

    class Meta:
        managed = False
        db_table = 'posts'
        app_label = 'post_data'

class PostTag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    tag_value = models.TextField(null=False, unique=True)

    class Meta:
        managed = False
        db_table = 'tags'
        app_label = 'tag_values'

class PostTagPivot(models.Model):
    post_id = models.IntegerField(primary_key=True)
    tag_id = models.IntegerField(null=False)

    class Meta:
        managed = False
        db_table = 'post_tag_pivot'
        app_label = 'post_tag_pivot_connector'