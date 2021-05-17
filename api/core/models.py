import uuid
import os

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, \
    BaseUserManager, PermissionsMixin
from django.conf import settings


def post_image_file_path(instance, filename):
    """Generate the filepath for the new image"""
    ext = filename.split(".")[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/recipe/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password, **kwargs):
        """
        Create a new user using email and password.
        This function optionally takes any additional fields
        passed to it into the kwargs
        :param email: The email with which the user wants to register
        :param password: Password string for the account
        :param kwargs: Any additional fields like super user flag.
        :return: User object
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Create a new super user using the email and password.
        :param email: Email address of the super user account
        :param password: Password for the account
        :return: superuser object
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model which supports email address instead of username.
    """

    email = models.EmailField(
        max_length=255,
        null=False,
        blank=False,
        unique=True
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    # Making the email field as the username field
    # instead of the original username field.
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


class Tag(models.Model):
    """Tag to be used for a blog post"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Post(models.Model):
    """Recipe object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    content = models.CharField(max_length=5000)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=post_image_file_path)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comment Objects"""
    class Meta:
        ordering = ['created_on']

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.CharField(max_length=5000)
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}_{self.post.title}'
