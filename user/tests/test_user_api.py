from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status 


def create_user(**params):
    return get_user_model().objects.create_user(**params)


CREATE_USER_URL = reverse('user:create')

CREATE_TOKEN_URL = reverse('user:token')

EDIT_USER_URL = reverse('user:edit')


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

    def test_token_create_success(self):
        '''
        Testing to create token for valdi user credentials successfully
        '''
        payload = {
            'email': 'test@test.com',
            'password': 'test123',
            'name': 'test name'
        }
        create_user(**payload)

        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_no_user(self):
        '''
        Test to obtain token for non-existing user
        '''
        payload = {
            'email': 'test@test.com',
            'password': 'test123',
            'name': 'test name'
        }
        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_invalid_password(self):
        '''
        Test obtaining token for user with invalid password
        '''
        payload = {
            'email': 'test@test.com',
            'password': 'test123',
            'name': 'test name'
        }
        create_user(**payload)

        res = self.client.post(CREATE_TOKEN_URL, {
            'email': 'test@test.com',
            'password': 'wrong'
        })        

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_blank_password(self):
        '''
        Test obtaining token for valid user with blank password
        '''
        payload = {
            'email': 'test@test.com',
            'password': 'test123',
            'name': 'test name'
        }
        create_user(**payload)

        res = self.client.post(CREATE_TOKEN_URL, {
            'email': 'test@test.com',
        })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_edit_unauthorized(self):
        '''
        Test retrieving edit url unauthorized fail
        '''
        res = self.client.get(EDIT_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPIUserTest(TestCase):
    '''
    Tests for authorized users
    '''
    def setUp(self):

        self.client = APIClient()
        self.user = create_user(
            email='test@test.com',
            password='test123',
            name='name'
        )
    
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile(self):
        '''
        Test retrieving authorized user profile
        '''
        res = self.client.get(EDIT_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': 'test@test.com',
            'name': 'name'
        })

    def test_post_edit_not_allowed(self):
        '''
        Test sending POST request to user edit url not allowed
        '''
        res = self.client.post(EDIT_USER_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_edit_profile_success(self):
        '''
        Test editting user profile is successful
        '''
        payload = {
            'password': 'newtest123',
            'name': 'newname'
        }
        res = self.client.patch(EDIT_USER_URL, payload)

        # Refresh self.user from DB
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))