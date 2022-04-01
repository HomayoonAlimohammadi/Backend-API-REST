from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status 


def create_user(**params):
    return get_user_model().objects.create_user(**params)

CREATE_USER_URL = reverse('user:create')


class PublicUserAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_user_creation(self):
        '''
        Test valid user created successfully (public)
        '''

        payload = {
            'email': 'test@test.com',
            'password': 'test123', 
            'name': 'Test User'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_duplicate_user_creation(self):
        '''
        Test to see if creating duplicate users fail
        '''
        payload = {
            'email': 'test@test.com',
            'password': 'test123', 
            'name': 'Test User'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        '''
        Test to see if the password is more than 8 characters.
        '''
        payload = {
            'email': 'test@test.com',
            'password': '123', 
            'name': 'Test User'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        
        self.assertFalse(user_exists)


