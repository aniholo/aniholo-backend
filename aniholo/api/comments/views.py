from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response

from . import models
from .utils import get_children, add_nodes
from aniholo import settings
from api.authentication import token
from api.authentication.models import User
from api.posts.models import Post, Vote


@csrf_exempt
@api_view(['POST'])
def create_comment(request):
    if 'access_token' not in request.POST or 'content' not in request.POST or 'post_id' not in request.POST:
        return Response({"status": "failed", "error": "must include token, content and post_id"})

    if not token.isValidToken(request.POST.get("access_token")):
        return Response({"status": "failed", "error": "invalid token"})

    payload = token.decode(request.POST.get("access_token"))

    user_id = payload.get('user_id')
    post_id = request.POST.get('post_id')
    parent_id = request.POST.get('parent_id')
    raw_content = request.POST.get('content')

    if parent_id is not None:
        try:
            parent = models.Comment.objects.get(comment_id=parent_id)
        except models.Comment.DoesNotExist:
            return Response({"status": "failed", "error": "parent comment does not exist"})
    else:
        parent = None

    try:
        post = Post.objects.get(post_id=post_id)
    except Post.DoesNotExist:
        return Response({"status": "failed", "error": "post does not exist"}) 

    comment = models.Comment(author=User.objects.get(user_id=user_id),
                   post=post,
                   parent=parent,
                   raw_content=raw_content)

    try:
        comment.save(force_insert=True)
        return Response({'status': 'success'})
    except:
        return Response({"status": "failed", "error": "internal server error"})


@csrf_exempt
@api_view(['POST'])
def edit_comment(request):
    if "access_token" not in request.POST or 'comment_id' not in request.POST or 'new_content' not in request.POST:
        return Response({"status": "failed", "error": "must include token, new content and comment id"})

    if not token.isValidToken(request.POST.get("access_token")):
        return Response({"status": "failed", "error": "invalid token"})

    payload = token.decode(request.POST.get("access_token"))
    comment_id = request.POST.get('comment_id')
    new_content = request.POST.get('new_content')

    comment = models.Comment.objects.filter(comment_id=comment_id).first()
    if comment is None:
        return Response({"status": "failed", "error": "comment doesn't exist"})

    if comment.status == 2:
        return Response({"status": "failed", "error": 'comment deleted, editing is forbidden'})

    if payload.get('user_id') == comment.author.user_id:
        comment.raw_content = new_content
        comment.status = 1
    else:
        return Response({"status": "failed", "error": 'user can edit only own comment'})

    try:
        comment.save()
        return Response({'status': 'success'})
    except:
        return Response({"status": "failed", "error": "internal server error"})


@csrf_exempt
@api_view(['POST'])
def delete_comment(request):
    if "access_token" not in request.POST or 'comment_id' not in request.POST:
        return Response({"status": "failed", "error": "must include token and comment id"})

    if not token.isValidToken(request.POST.get("access_token")):
        return Response({"status": "failed", "error": "invalid token"})

    payload = token.decode(request.POST.get("access_token"))
    comment_id = request.POST.get('comment_id')

    comment = models.Comment.objects.filter(comment_id=comment_id).first()
    if comment is None:
        return Response({"status": "failed", "error": "comment doesn't exist"})

    if payload.get('user_id') != comment.author.user_id:
        return Response({"status": "failed", "error": 'user can only delete own comment'})

    comment.status = 2
    try:
        comment.save()
        return Response({'status': 'success'})
    except:
        return Response({"status": "failed", "error": "internal server error"})


@csrf_exempt
@api_view(['POST'])
def get_comment(request):
    if "access_token" not in request.POST or 'comment_id' not in request.POST:
        return Response({"status": "failed", "error": "must include token and comment id"})

    if not token.isValidToken(request.POST.get("access_token")):
        return Response({"status": "failed", "error": "invalid token"})

    payload = token.decode(request.POST.get("access_token"))
    user_id = payload.get("user_id")

    try:
        comment_id = int(request.POST.get('comment_id'))
        depth = int(request.POST.get('depth', 10))
        order_type = request.POST.get('order_type', 'best')
    except:
        return Response({"status": "failed", "error": "parameter error"})

    comment = models.Comment.objects.filter(comment_id=comment_id).first()
    if comment is None:
        return Response({"status": "failed", "error": "comment doesn't exist"})

    vote = Vote.objects.filter(user_id=user_id, vote_type=0, object_id=comment.comment_id).first()
    if vote is None:
        vote = 0
    else:
        vote = vote.vote_value

    if comment.status == 2:
        tree = {'comment_id': comment.comment_id,
                'author_id': "[deleted]",
                'author_name': "[deleted]",
                'date_posted': "[deleted]",
                'score': "[deleted]",
                'user_vote': "[deleted]",
                'content': "[deleted]",
                'children': []}
    else:
        tree = {'comment_id': comment.comment_id,
                'author_id': comment.author.user_id,
                'author_name': comment.author.username,
                'date_posted': comment.date_posted,
                'score': comment.score,
                'user_vote': vote,
                'content': comment.raw_content,
                'parent_id': comment.parent_id,
                'children': []}
    add_nodes(get_children(comment, order_type), tree, user_id, 1, depth, order_type)
    return Response({'status': 'success', 'tree': tree})
