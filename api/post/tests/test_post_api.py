import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Post, Tag

from post.serializers import PostSerializer, PostDetailSerializer

POSTS_URL = reverse('post:post-list')


def image_upload_url(post_id):
    """
    Helper method to retrieve the API end-point to upload the image.
    :param post_id: The unique ID of the post we want to add image to.
    :return: An end-point to which we can POST an image
    """
    return reverse('post:post-upload-image', args=[post_id])


def detail_url(post_id):
    """
    Helper method to retrieve the API end-point to post content
    :param post_id: The unique ID of the post
    :return: An end-point to retrieve the post content.
    """
    return reverse('post:post-detail', args=[post_id])


def sample_tag(user, name="Technology"):
    """
    Helper method to create a tag and return the tag object
    :param user: user that created the tag.
    :param name: name of the tag
    :return: Returns a tag object after creating it.
    """
    return Tag.objects.create(user=user, name=name)


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


class PublicPostAPITests(TestCase):
    """
    Test cases for unauthenticated access to the post API
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that the authentication is required!
        :return: None
        """
        res = self.client.get(POSTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePostAPITests(TestCase):
    """
    Test cases for authenticated access to the post API
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@test.com',
            'Test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_posts(self):
        """
        Test case for retrieving the list of posts
        :return: None
        """
        sample_post_title = {'title': 'Sample Post 01'}
        sample_post(user=self.user, **sample_post_title)

        sample_post_title = {'title': 'Sample Post 02'}
        sample_post(user=self.user, **sample_post_title)

        res = self.client.get(POSTS_URL)

        posts = Post.objects.all().order_by('id')
        serializer = PostSerializer(posts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_post_detail(self):
        """
        Test viewing of a post details.
        :return: None
        """
        post = sample_post(user=self.user)
        post.tags.add(sample_tag(user=self.user))

        url = detail_url(post.id)
        res = self.client.get(url)

        serializer = PostDetailSerializer(post)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_post(self):
        """
        Test creating a post
        :return: None
        """
        payload = {
            'title': 'Blog post 01',
            'content': 'Content for blog post 01'
        }

        res = self.client.post(POSTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(post, key))

    def test_create_recipe_with_tags(self):
        """
        Test the creation of a post with tags
        """
        tag1 = sample_tag(user=self.user, name="Technology")
        tag2 = sample_tag(user=self.user, name="Python")

        payload = {
            'title': 'Blog Post 01',
            'content': 'Content for blog post 01',
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(POSTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(id=res.data['id'])
        tags = post.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_partial_update_post(self):
        """
        Test updating post with PATCH
        """
        post = sample_post(user=self.user)
        post.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name="Django")

        payload = {'title': 'Python + Django', 'tags': [new_tag.id]}
        url = detail_url(post.id)
        self.client.patch(url, payload)

        post.refresh_from_db()
        self.assertEqual(post.title, payload['title'])
        tags = post.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_post(self):
        """
        Test updating a post with PUT
        """
        post = sample_post(user=self.user)
        post.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Blog Post 007',
            'content': 'Content for blog post 007',
        }
        url = detail_url(post.id)
        self.client.put(url, payload)

        post.refresh_from_db()
        self.assertEqual(post.title, payload['title'])
        tags = post.tags.all()
        self.assertEqual(len(tags), 0)

#
# class PostImageUploadTests(TestCase):
#
#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user(
#             'user@test.com',
#             'Test123'
#         )
#         self.client.force_authenticate(self.user)
#         self.post = sample_post(user=self.user)
#
#     def tearDown(self):
#         """
#         We have to delete the created dummy images to ensure
#         we are maintaining the system state correctly after
#         the test execution.
#         :return: None
#         """
#         self.post.image.delete()
#
#     def test_uploading_valid_image(self):
#         """
#         Test Uploading a valid image file
#         """
#         url = image_upload_url(self.post.id)
#         with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
#             img = Image.new('RGB', (10, 10))
#             img.save(ntf, format='JPEG')
#             ntf.seek(0)
#             res = self.client.post(url, {'image': ntf}, format='multipart')
#
#         self.post.refresh_from_db()
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertIn('image', res.data)
#         self.assertTrue(os.path.exists(self.post.image.path))
#
#     def test_uploading_invalid_image(self):
#         """
#         Test uploading an invalid image file
#         """
#         url = image_upload_url(self.post.id)
#         res = self.client.post(url,
#                                {'image': 'notanimage'},
#                                format='multipart'
#                                )
#
#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestPostFilteringAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@test.com',
            'Test123'
        )
        self.client.force_authenticate(self.user)

    def test_filter_recipes_by_tags(self):
        """Test returning posts with specific tags"""
        post1 = sample_post(user=self.user, title='Blog Post 01')
        post2 = sample_post(user=self.user, title='Blog Post 02')

        tag1 = sample_tag(user=self.user, name='Technology')
        tag2 = sample_tag(user=self.user, name='Frameworks')

        post1.tags.add(tag1)
        post2.tags.add(tag2)

        post3 = sample_post(user=self.user, title='Blog Post 03')

        res = self.client.get(
            POSTS_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = PostSerializer(post1)
        serializer2 = PostSerializer(post2)
        serializer3 = PostSerializer(post3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
