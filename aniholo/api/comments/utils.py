from .models import Comment
from api.posts.models import Vote

def add_nodes(q_set, tree, user_id, current_depth, depth, order_type):
    ''' recursive tree building '''
    if q_set is None or current_depth == depth:
        return None
    i = 0
    for node in q_set:
        vote = Vote.objects.filter(user_id=user_id, vote_type=0, object_id=node.comment_id).first()
        if vote is None:
            vote = 0
        else:
            vote = vote.vote_value
        if node.status == 2:
            tree['children'].append({'comment_id': node.comment_id,
                                     'author_id': "[deleted]",
                                     'author_name': "[deleted]",
                                     'date_posted': "[deleted]",
                                     'score': "[deleted]",
                                     'user_vote': "[deleted]",
                                     'content': "[deleted]",
                                     'children': []})
        else:
            tree['children'].append({'comment_id': node.comment_id,
                                     'author_id': node.author.user_id,
                                     'author_name': node.author.username,
                                     'date_posted': node.date_posted,
                                     'score': node.score,
                                     'user_vote': vote,
                                     'content': node.raw_content,
                                     'parent_id': node.parent_id,
                                     'children': []})
        add_nodes(get_children(node, order_type), tree['children'][i], user_id, current_depth + 1, depth, order_type)
        i += 1


def get_children(node, order_type):
    comments = Comment.objects.filter(parent_id=node.comment_id)
    if order_type == 'best':
        return comments.order_by('-score')
    else:
        return comments.order_by('-date_posted')
