from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response

from . import models
from aniholo import settings
from api.authentication import token
from api.authentication.models import User
from api.posts.models import Post, Comment


@csrf_exempt
@api_view(['POST'])
def create_comment(request):
    if "token" not in request.POST or "content" not in request.POST:
        return Response({"status": "failed", "error": "must include token, title, content and content type"})

    if not token.isValidToken(request.POST.get("token")):
        return Response({"status": "failed", "error": "invalid token"})

    payload = token.decode(request.POST.get("token"))

    try:
        user_id = payload.get("user_id")
        post_id = request.POST.get('post_id')
        parent_id = request.POST.get('parent_id')
        raw_content = request.POST.get("content")
    except:
        return Response({"status": "failed", "error": "parameter error"})

    if parent_id is not None:
        parent = Comment.objects.get(comment_id=parent_id)
    else:
        parent = None

    post = Comment(author=User.objects.get(user_id=user_id),
                   post=Post.objects.get(post_id=post_id),
                   parent=parent,
                   raw_content=raw_content)

    try:
        post.save(force_insert=True)
        return Response({'status': 'success'})
    except:
        return Response({"status": "failed", "error": "internal server error"})
