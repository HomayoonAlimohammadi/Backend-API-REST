from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                       PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        '''
        Creates and saves a new user
        '''
        user = self.model(email=email, **extra_fields) # this is equal to making a new user model instance
        user.set_password(password) # user password can not and should not be accessed raw

        # not necessary, but good practice
        user.save(using=self._db) # supporting multiple databases

        return user


class User(AbstractBaseUser, PermissionsMixin):

    '''
    Custom user model that supports using email instead of username
    '''

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager() # what is this exactly?

    USERNAME_FIELD = 'email' # this makes our user model custom

        
