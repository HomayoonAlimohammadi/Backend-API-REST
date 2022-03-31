from django.test import TestCase
from django.contrib.auth import get_user_model  


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
            get_user_model().objects.create_superuser(
                email='test@test.com', password=None)
        
            
            