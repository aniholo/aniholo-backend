from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError
from django.db.models import Count
from django.utils.dateformat import format
from rest_framework.decorators import api_view

from . import models
from aniholo import settings
from api.authentication import token
from api.comments.utils import get_children, add_nodes
from api.authentication.models import User
from api.comments.models import Comment

import time
import ast
from types import SimpleNamespace

@csrf_exempt
@api_view(['POST'])
def create_post(request):
	if "token" not in request.POST or "title" not in request.POST or "content" not in request.POST or "content_type" not in request.POST:
		return Response({"status": "failed", "error": "must include token, title, content and content type"})

	if not token.isValidToken(request.POST.get("token")):
		return Response({"status": "failed", "error": "invalid token"})

	payload = token.decode(request.POST.get("token"))

	try:
		user_id = payload.get("user_id")
		title = request.POST.get("title")
		raw_content = request.POST.get("content")
		content_type = int(request.POST.get("content_type"))
		tags = str(request.POST.get("tags", "")).split(",")
	except:
		return Response({"status": "failed", "error": "parameter error"})

	post = models.Post(author=User.objects.get(user_id=user_id), title=title,
						raw_content=raw_content, content_type=content_type)

	try:
		post.save(force_insert=True)

		for tag in tags:
			tag, _ = models.Tag.objects.get_or_create(tag_value=tag)
			tag.post.add(post)

		return Response({'status': 'success'})
	except:
		return Response({"status": "failed", "error": "internal server error"})

@csrf_exempt
@api_view(['POST'])
def get_post(request):
	if "token" not in request.POST or "id" not in request.POST:
		return Response({"status": "failed", "error": "must include token and post id"})

	if not token.isValidToken(request.POST.get("token")):
		return Response({"status": "failed", "error": "invalid token"})

	payload = token.decode(request.POST.get("token"))

	user_id = payload.get("user_id")

	try:
		post = models.Post.objects.get(post_id=request.POST.get("id"))
		try:
			vote = models.Vote.objects.get(user_id=user_id, vote_type=0, object_id=post.post_id).vote_value
		except models.Vote.DoesNotExist:
			vote = 0
		return Response({'status': 'success', 'post': {
			'post_id': post.post_id,
			'author_id': post.author_id,
			'author_name': post.author.username or post.author_id,
			'date_posted': post.date_posted,
			'score': post.score,
			'user_vote': vote,
			'title': post.title,
			'content_type': post.content_type,
			'content': post.raw_content,
			'tags': [tag.tag_value for tag in post.tag_set.all()]
		}})
	except models.Post.DoesNotExist:
		return Response({"status": "failed", "error": "no matching post found"})
	except:
		return Response({"status": "failed", "error": "internal server error"})

@csrf_exempt
@api_view(['POST'])
def vote(request):
	if "token" not in request.POST or "id" not in request.POST or "type" not in request.POST or "value" not in request.POST:
		return Response({"status": "failed", "error": "must include token, object id, object type and vote value"})

	if not token.isValidToken(request.POST.get("token")):
		return Response({"status": "failed", "error": "invalid token"})

	payload = token.decode(request.POST.get("token"))

	user_id = payload.get("user_id")

	try:
		object_type = int(request.POST.get("type"))
		object_id = int(request.POST.get("id"))
		vote_value = int(request.POST.get("value"))
	except:
		return Response({"status": "failed", "error": "parameter error"})

	try:
		vote, _ = models.Vote.objects.get_or_create(user_id=user_id, vote_type=object_type, object_id=object_id)
		update_value = vote_value - vote.vote_value
		if update_value != 0:
			if object_type == 0:
				post = models.Post.objects.get(post_id=object_id)
				post.score += update_value
				post.save(force_update=True)
			else:
				comment = Comment.objects.get(comment_id=object_id)
				comment.score += update_value
				comment.save(force_update=True)
			vote.vote_value = vote_value
			vote.save(force_update=True)
		return Response({'status': 'success'})
	except (models.Post.DoesNotExist, Comment.DoesNotExist):
		return Response({"status": "failed", "error": "no matching object found"})
	except:
		return Response({"status": "failed", "error": "internal server error"})

@csrf_exempt
@api_view(['POST'])
def list_posts(request):
	if "token" not in request.POST:
		return Response({"status": "failed", "error": "must include token and post id"})

	if not token.isValidToken(request.POST.get("token")):
		return Response({"status": "failed", "error": "invalid token"})

	payload = token.decode(request.POST.get("token"))
	user_id = payload.get("user_id")

	try:
		tags = request.POST.get("tags", "").split(",")
		order = request.POST.get("sort", "relevance")
		limit = int(request.POST.get("limit", 20))
		limit = limit if limit < 100 else 20
		begin_from = int(request.POST.get("from", 0))
	except:
		return Response({"status": "failed", "error": "parameter error"})

	no_vote = SimpleNamespace(vote_value=0)

	try:
		posts = models.Post.objects.all()

		if tags[0]:
			# count = number of matched tags
			posts = posts.filter(tag__in=[tag.id for tag in models.Tag.objects.filter(tag_value__in=tags)]).annotate(count=Count("post_id")).distinct()

		if order == "newest":
			posts = posts.order_by("-date_posted")
		elif order == "oldest":
			posts = posts.order_by("date_posted")
		elif order == "top":
			posts = posts.order_by("-score", "-date_posted")
		else:
			posts = posts.order_by("-count", "-date_posted")
			pass  # haven't found a way to do this yet, relevance should depend on a combination age and score as well (rn only on number of matched tags and age if equal)

		return Response({'status': 'success', 'posts': [{
			'post_id': post.post_id,
			'author_id': post.author_id,
			'author_name': post.author.username or post.author_id,
			'date_posted': post.date_posted,
			'score': post.score,
			'user_vote': (models.Vote.objects.filter(user_id=user_id, vote_type=0, object_id=post.post_id).first() or no_vote).vote_value,
			'title': post.title,
			'content_type': post.content_type,
			'content': post.raw_content,
			'tags': [tag.tag_value for tag in post.tag_set.all()]
		} for post in posts[begin_from:limit]]})
	except:
		return Response({"status": "failed", "error": "internal server error"})


@csrf_exempt
@api_view(['POST'])
def list_comment(request):
	if "access_token" not in request.POST or 'post_id' not in request.POST:
		return Response({"status": "failed", "error": "must include token and post id"})

	if not token.isValidToken(request.POST.get("access_token")):
		return Response({"status": "failed", "error": "invalid token"})

	payload = token.decode(request.POST.get("access_token"))
	user_id = payload.get("user_id")

	try:
		post_id = int(request.POST.get('post_id'))
		depth = int(request.POST.get('depth', 10))
		order_type = request.POST.get('order_type', 'best')
		limit = int(request.POST.get('limit', 20))
	except:
		return Response({"status": "failed", "error": "parameter error"})
	comments = Comment.objects.filter(post_id=post_id, parent_id=None)
	if order_type == 'best':
		comments = comments.order_by('-score', 'comment_id')[:limit]
	else:
		comments = comments.order_by('-date_posted', 'comment_id')[:limit]

	i = 0
	tree = []
	for comment in comments:
		if comment.status == 2:
			tree.append(
				{'comment_id': comment.comment_id,
				 'author_id': "[deleted]",
				 'author_name': "[deleted]",
				 'date_posted': "[deleted]",
				 'score': "[deleted]",
				 'user_vote': "[deleted]",
				 'content': "[deleted]",
				 'children': []}
			)
		else:
			vote = models.Vote.objects.filter(user_id=user_id, vote_type=0, object_id=comment.comment_id).first()
			if vote is None:
				vote = 0
			else:
				vote = vote.vote_value
			tree.append(
				{'comment_id': comment.comment_id,
				 'author_id': comment.author.user_id,
				 'author_name': comment.author.username,
				 'date_posted': comment.date_posted,
				 'score': comment.score,
				 'user_vote': vote,
				 'content': comment.raw_content,
				 'parent_id': comment.parent_id,
				 'children': []}
				)
		add_nodes(get_children(comment, order_type), tree[i], user_id, 1, depth, order_type)
		i += 1
	return Response({"status": "success", 'tree': tree})
