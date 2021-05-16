from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Post

from post.serializers import TagSerializer

TAGS_URL = reverse('post:tag-list')


class PublicTagAPITests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test case to check that the login is required to retrieve tags
        :return: None
        """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    """
    Test the authorized user tags API
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'user@test.com',
            'Test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """
        Test case to validate the tags retrieval for a logged in user
        :return: None
        """
        Tag.objects.create(user=self.user, name="Languages")
        Tag.objects.create(user=self.user, name="Frameworks")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """
        Test case to check that the tags returned are by
        the authenticated user only.
        :return: None
        """
        user2 = get_user_model().objects.create_user(
            'user02@test.com',
            'Test123'
        )
        Tag.objects.create(user=user2, name="Languages")
        tag = Tag.objects.create(user=self.user, name="Frameworks")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """
        Test creating a new tag
        :return: None
        """
        payload = {'name': 'Languages'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """
        Test creating an invalid tag
        :return: None
        """
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_posts(self):
        """
        Filtering tags that are currently assigned to some post.
        We need to ensure that tags that are not added to any
        blog post not returned to reduce the response size and
        ensure the UI is better.
        :return: None
        """
        tag1 = Tag.objects.create(user=self.user, name='Frameworks')
        tag2 = Tag.objects.create(user=self.user, name='Languages')

        post = Post.objects.create(
            user=self.user,
            title='Introduction to Django Framework',
            content='Some random content to fill this!',
        )
        post.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_asigned_unique(self):
        """
        Test filtering of tags by assigned user and
        returns unique items without duplicates
        :return: None
        """
        tag = Tag.objects.create(user=self.user, name='Frameworks')
        Tag.objects.create(user=self.user, name='Languages')

        post1 = Post.objects.create(
            user=self.user,
            title='Introduction to Django Framework - Part 01',
            content='Some random content to fill this!',
        )
        post1.tags.add(tag)

        post2 = Post.objects.create(
            user=self.user,
            title='Introduction to Django Framework - Part 02',
            content='Some random content to fill this!',
        )
        post2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)