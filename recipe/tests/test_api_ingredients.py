from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

from django.urls import reverse 


INGREDIENTS_URL = reverse('recipe:ingredient-list')

class PublicIngredientAPITests(TestCase):

    def setUp(self):

        self.client = APIClient()
        

    def test_ingredients_retrieve_unauthorized_fail(self):
        '''
        Test retrieving ingredients with unauthorized request fail
        '''

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):

    def setUp(self):

        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='test123',
            name='test user'
        )
        self.client.force_authenticate(self.user)
    
    def test_retrieve_ingredients_authorized_success(self):
        '''
        Test retrieving ingredients with authenticated user 
        is successful
        '''
        payload = {
            'name': 'ingredient 1',
            'user': self.user,
        }
        Ingredient.objects.create(**payload)

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], payload['name'])

        