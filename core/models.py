from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin


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