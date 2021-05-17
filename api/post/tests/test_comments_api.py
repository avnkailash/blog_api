from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Post, Comment

from post.serializers import CommentSerializer, CommentDetailSerializer

COMMENTS_URL = reverse('post:comment-list')


def comment_url(comment_id):
    """
    Helper method to retrieve the API end-point to post content
    :param comment_id: The unique ID of the post
    :return: An end-point to retrieve the post content.
    """
    return reverse('post:comment-detail', args=[comment_id])


def sample_post(user, **params):
    """
    Helper method to create a sample post for our testing purposes.
    :param user:
    :param params:
    :return: A Post object after it is created.
    """
    defaults = {
        'title': 'Blog Post #01',
        'content': 'Blog post\'s content that is really awesome',
    }
    defaults.update(params)

    return Post.objects.create(user=user, **defaults)


def sample_comment(user, post, **params):
    """
    Helper method to create a sample comment for a given post
    :param user: The user who is creating this comment
    :param post: The post to which this comment is associated with.
    :param params: Any additional arguments to modify the comment object
    :return: None
    """
    defaults = {
        'content': 'This is a sample comment'
    }
    defaults.update(**params)

    return Comment.objects.create(user=user, post=post, **defaults)


class PublicCommentsAPITests(TestCase):
    """
    Test cases for unauthenticated access to the comments API
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that the authentication is required!
        :return: None
        """
        res = self.client.get(COMMENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePostAPITests(TestCase):
    """
    Test cases for authenticated access to the comments API
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@test.com',
            'Test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_comments(self):
        """
        Test case for retrieving the list of comments
        :return: None
        """
        sample_post_title = {'title': 'Sample Post 01'}
        post = sample_post(user=self.user, **sample_post_title)

        comment = {'content': 'Comment for the sample post 01'}
        sample_comment(user=self.user, post=post, **comment)

        res = self.client.get(COMMENTS_URL)

        comments = Comment.objects.all().order_by('id')
        serializer = CommentSerializer(comments, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_comment_detail(self):
        """
        Test viewing of a post details.
        :return: None
        """
        post = sample_post(user=self.user)

        sample_comment_data = {'content': 'Comment for the sample post 01'}
        comment = sample_comment(
            user=self.user,
            post=post,
            **sample_comment_data
        )

        url = comment_url(comment.id)
        res = self.client.get(url)

        serializer = CommentDetailSerializer(comment)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_comment(self):
        """
        Test creating a comment
        :return: None
        """
        post = sample_post(user=self.user)

        comment_payload = {
            'content': 'Creating a new comment using the comment API',
            'post': post.id
        }

        res = self.client.post(COMMENTS_URL, comment_payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(id=res.data['id'])
        for key in comment_payload.keys():
            if key == 'post':
                post = Post.objects.get(id=comment_payload[key])
                self.assertEqual(post, getattr(comment, key))
            else:
                self.assertEqual(comment_payload[key], getattr(comment, key))

    def test_update_comment(self):
        """
        Test updating comment with PATCH
        """
        post = sample_post(user=self.user)
        old_comment_payload = {
            'content': 'This is old comment!',
        }
        comment = sample_comment(
            user=self.user,
            post=post,
            **old_comment_payload
        )
        new_comment_payload = {
            'content': 'This is the updated comment'
        }

        url = comment_url(comment.id)
        self.client.patch(url, new_comment_payload)

        comment.refresh_from_db()
        self.assertEqual(comment.content, new_comment_payload['content'])
