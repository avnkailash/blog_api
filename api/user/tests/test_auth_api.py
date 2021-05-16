from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_sample_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicAuthAPITests(TestCase):
    """Tests the authentication public API """

    def setUp(self):
        """
        The required set up for our tests to work correctly.
        """
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        Test creation of a user account with valid payload.
        We expect a successful test execution
        :return: None
        """
        payload = {
            'email': 'user@test.com',
            'name': 'Name',
            'password': 'Test123'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_already_exists(self):
        """
        Test case to create a user using an email address
        already registered
        :return: None
        """
        payload = {
            'email': 'user@test.com',
            'name': 'Name',
            'password': 'Test123'
        }
        create_sample_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        Test case to check if the password has
        met the requirements put by our system
        :return: None
        """
        payload = {
            'email': 'user@test.com',
            'name': 'Name',
            'password': 'TT'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Now check if the user exists in the DB.
        # User must not be created hence should not exist in our DB
        exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(exists)

    def test_create_token_valid_credentials(self):
        """
        Test case to validate the token is created for a valid login attempt
        :return: None
        """
        payload = {
            'email': 'user@test.com',
            'password': 'Test123'
        }
        create_sample_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
        Test case to validate the token is created for
        an invalid login attempt
        :return: None
        """
        payload = {
            'email': 'user@test.com',
            'password': 'Test123'
        }
        create_sample_user(**payload)

        payload['password'] = 'Wrong Pasword'
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Test that the token creation fails for a login attempt
        where the user is not yet registered
        :return: None
        """
        payload = {
            'email': 'user@test.com',
            'password': 'Test123'
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_password(self):
        """
        Test that email and password are required fields
        :return: None
        """
        payload = {
            'email': 'user@test.com',
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """
        Test that authentication is required for users
        :return: None
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAuthAPITests(TestCase):
    """
    Test API requests that require authentication
    """

    def setUp(self):
        self.user = create_sample_user(
            email='user@test.com',
            password='Test123',
            name='Test User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        Test case to retrieve profile for logged in user
        :return: None
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """
        Test case to validate that the POST is not allowed on ME URL
        :return: None
        """
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
        Test case to update the user profile for authenticated users.
        :return: None
        """
        payload = {
            'name': 'New Name',
            'password': 'SuperStrongPassword123'
        }

        res = self.client.patch(ME_URL, payload)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)