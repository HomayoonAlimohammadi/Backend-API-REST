from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.conf import settings
import uuid
import os


def recipe_image_field_url(instance, filename):
    '''
    Generate url for the recipe image field
    '''
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/recipe/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        '''
        Creates and saves a new user
        '''

        if not email:
            raise ValueError('Email must be provided.')

        # this is equal to making a new user model instance
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # password can not and should not be accessed without being encrypted
        user.set_password(password)

        # not necessary, but good practice
        user.save(using=self._db)  # supporting multiple databases

        return user

    def create_superuser(self, email, password):
        '''
        Creates and saves a new super user
        '''
        if not password:
            raise ValueError('Super user must have a password.')

        superuser = self.create_user(email, password)
        superuser.is_staff = True
        superuser.is_superuser = True

        superuser.save(using=self._db)

        return superuser


class User(AbstractBaseUser, PermissionsMixin):

    '''
    Custom user model that supports using email instead of username
    '''

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()  # what is this exactly?
    # This makes it so that we can say objects.create_user
    # since UserManages has the create_user method.

    USERNAME_FIELD = 'email'  # this makes our user model custom


class Tag(models.Model):

    name = models.CharField(max_length=30)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tags',
        )

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ingredients',
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):

    title = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    time_minutes = models.IntegerField(default=10)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=999)
    link = models.CharField(max_length=255, blank=True)
    image = models.ImageField(null=True, upload_to=recipe_image_field_url)

    # using string for the manytomany model instead of the model itself
    # makes it so we don't have to order them correctly
    # otherwise we would have to place Recipe below both Ingredient and
    # Tag model.
    ingredients = models.ManyToManyField(
        'Ingredient',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='tags'
    )

    def __str__(self):
        return self.title