from django.test import TestCase
from django.contrib.auth import get_user_model  


class ModelTests(TestCase):

    def test_create_user_with_email_successfully(self):
        '''
        Test creating a user with email is successful
        '''
        email = 'test@test.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(
            email=email,
            password = password
        )

        query = get_user_model().objects.all()     
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password)) # user password can not be accessed directly
        self.assertEqual(query.count(), 1)