from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

from django.urls import reverse


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def sample_user(email='sample@test.com',
                password='sample123',
                name='sample user'):
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        name=name
    )


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
        Ingredient.objects.create(user=self.user, name='ingrd1')
        Ingredient.objects.create(user=self.user, name='ingrd2')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_ingredients_limited_to_user(self):
        '''
        Test retrieving only the ingredients that are of
        property of the request user and nothing more
        '''
        sampleUser = sample_user()
        Ingredient.objects.create(user=sampleUser, name='ingrd1')

        ingredient = Ingredient.objects.create(user=self.user, name='ingrd2')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredients_success(self):
        '''
        Test creating ingredients by authorized user is successful
        '''
        payload = {
            'name': 'ingrd1',
        }

        res = self.client.post(INGREDIENTS_URL, payload)
        exists = Ingredient.objects.filter(
            name=payload['name'],
            user=self.user
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_invalid_ingredients_fail(self):
        '''
        Test creating ingredients without a name fail
        '''
        payload = {
            'name': '',
        }

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_creating_duplicate_ingredients_by_user_fail(self):
        '''
        Test creating ingredients with duplicate names
        by the same user fail
        '''
        payload = {
            'name': 'ingredient 1',
            'user': self.user
        }
        Ingredient.objects.create(**payload)

        with self.assertRaises(ValueError):
            self.client.post(INGREDIENTS_URL, payload)