from django.test import TestCase
from django.contrib.auth import get_user_model


def sample_user(email='user@test.com', password='Test123'):
    """
    Helper method to create a sample user for our test cases!
    :param email: Email address of the sample user
    :param password: A password for account creation.
    This can be a weak password as well since this is restricted
    to our testing environment.
    :return: Returns the created user object
    """

    # We will be relying on the get_user_model() from
    # the auth module to ensure that the user model
    # can be switched in future without any new bugs getting introduced.
    return get_user_model().objects.create_user(email, password)


class ModelTestScenarios(TestCase):
    """A testing class that holds all the test cases specific to models."""

    def test_create_user_with_email_successful(self):
        """
        A test case to check the creation of a user account
        with valid details provided.
        :return: None
        """
        email = 'testUser@test.com'
        password = 'Test123'

        user = sample_user(email=email, password=password)

        # Assertions to check if the results are as expected.
        self.assertEqual(user.email, email)

        # We cannot check the password just like an email field.
        # We have to rely on the check_password helper method of
        # the user object
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        A test to validate if the email string is normalized for a new user
        :return: None
        """
        email = 'user@TEST.COM'
        user = sample_user(email=email)

        # Checking if the email in the user object is normalized
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """
        A test to create uesr with invalid email.
        We should see a ValueError in such cases.
        :return: None
        """
        with self.assertRaises(ValueError):
            sample_user(email=None)

    def test_create_new_super_user(self):
        """
        A test to check if super user creation is working as expected
        :return: None
        """
        user = get_user_model().objects.create_superuser(
            'moderator@test.com',
            'Moderator123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)