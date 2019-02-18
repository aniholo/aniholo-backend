from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.


class Comment(MPTTModel):
    comment_id = models.AutoField(primary_key=True)
    author = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    raw_content = models.TextField()
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(default=0)  # 0 - default, 1 - edited, 2 - deleted

    class MPTTMeta:
        order_by_insertion = ['-score']

    class Meta:
        db_table = 'comments'

