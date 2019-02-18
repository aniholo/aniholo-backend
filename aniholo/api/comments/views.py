from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response

from . import models
from aniholo import settings
from api.authentication import token
from api.authentication.models import User
from api.posts.models import Post


@csrf_exempt
@api_view(['POST'])
def create_comment(request):
    if 'access_token' not in request.POST or "content" not in request.POST:
        return Response({"status": "failed", "error": "must include token, title, content and content type"})

    if not token.isValidToken(request.POST.get("access_token")):
        return Response({"status": "failed", "error": "invalid token"})

    payload = token.decode(request.POST.get("access_token"))

    user_id = payload.get("user_id")
    post_id = request.POST.get('post_id')
    parent_id = request.POST.get('parent_id')
    raw_content = request.POST.get("content")

    if parent_id is not None:
        parent = models.Comment.objects.get(comment_id=parent_id)
    else:
        parent = None

    comment = models.Comment(author=User.objects.get(user_id=user_id),
                   post=Post.objects.get(post_id=post_id),
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

    try:
        comment = models.Comment.objects.get(comment_id=comment_id)
    except:
        return Response({"status": "failed", "error": "comment doesn't exist"})

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
        return Response({"status": "failed", "error": "must include token, new content and comment id"})

    if not token.isValidToken(request.POST.get("access_token")):
        return Response({"status": "failed", "error": "invalid token"})

    payload = token.decode(request.POST.get("access_token"))
    comment_id = request.POST.get('comment_id')

    try:
        comment = models.Comment.objects.get(comment_id=comment_id)
    except:
        return Response({"status": "failed", "error": "comment doesn't exist"})

    if payload.get('user_id') != comment.author.user_id:
        return Response({"status": "failed", "error": 'user can edit only own comment'})

    comment.status = 2
    try:
        comment.save()
        return Response({'status': 'success'})
    except:
        return Response({"status": "failed", "error": "internal server error"})
