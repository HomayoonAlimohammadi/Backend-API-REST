from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='test@test.com', password='test123'):
    return get_user_model().objects.create_user(
        email=email, 
        password=password,
        )


class ModelTests(TestCase):

    def test_create_user_with_email_successfully(self):
        '''
        Test creating a user with email is successful.
        '''
        email = 'test@test.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        query = get_user_model().objects.all()     
        self.assertEqual(user.email, email)

        # user password can not be accessed directly
        self.assertTrue(user.check_password(password))
        self.assertEqual(query.count(), 1)

    def test_normalize_user_email(self):
        '''
        Testing to see if user email is normalized or not.
        '''
        email = 'test@TEST.COM'
        password = 'test123'

        user = get_user_model().objects.create_user(email, password)
        self.assertEqual(user.email, email.lower())

    def test_new_user_email_not_blank(self):
        '''
        Testing to make sure users can not be created with blank or null email.
        '''
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')
        
    def test_create_new_superuser(self):
        '''
        Testing create_superuser to have certain permissions
        '''
        superuser = get_user_model().objects.create_superuser(
            'test@test.com',
            'test123'
        )

        self.assertTrue(
            superuser.is_superuser and superuser.is_staff
        )

    def test_new_superuser_no_email_or_password(self):
        '''
        Testing make sure super user has both valid email and password
        '''

        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                email='', password='test123')

        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                email='test@test.com', password=None)

    def test_tag_string(self):
        '''
        Test string representation of tag is OK
        '''
        user = sample_user()
        tag = models.Tag.objects.create(
            user=user,
            name='tag'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_string(self):
        '''
        Test string representation of the ingredients
        match their name
        '''
        user = sample_user()
        payload = {
            'user': user,
            'name': 'ingredient 1',
        }
        ingredient = models.Ingredient.objects.create(**payload)
        
        self.assertEqual(str(ingredient), payload['name'])

    def test_recipe_string(self):
        '''
        Test string representation of the recipes is their name
        '''
        user = sample_user()
        payload = {
            'title': 'recipe 1',
            'user': user,
            'time_minutes': 20,
            'price': 1.00
        }
        recipe = models.Recipe.objects.create(**payload)

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_image_field_url(self, mock_function):
        '''
        Test url generator for the image field
        '''
        uuid_return = 'test-image'
        mock_function.return_value = uuid_return

        url = models.recipe_image_field_url(None, 'mytestimage.jpg')
        exp_url = f'uploads/recipe/{uuid_return}.jpg'

        self.assertEqual(url, exp_url)