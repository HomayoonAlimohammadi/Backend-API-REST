from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Ingredient, Tag
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def recipe_detail_url(recipe):
    return reverse('recipe:recipe-detail', args=[recipe.id])


def sample_user(email='sample@test.com',
                password='sample123',
                name='sample name'):
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        name=name
    )


class PublicRecipeAPITests(TestCase):
    '''
    Tests for public api recipe
    '''
    
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_recipe_unauthorized(self):
        '''
        Test retrieving recipes unauthorized fail
        '''
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_recipe_detail_unauthorized(self):
        '''
        Test retrieving recipe detail by unauthorized user fail
        '''
        sampleUser = sample_user()
        recipe = Recipe.objects.create(
            title='recipe 1',
            price=1.00,
            time_minutes=1,
            user=sampleUser,
        )
        
        url = recipe_detail_url(recipe)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            name='test user',
            email='test@test.com',
            password='test123',
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.ingredient_1 = Ingredient.objects.create(
            name='test ingredient 1',
            user=self.user
        )
        self.ingredient_2 = Ingredient.objects.create(
            name='test ingredient 2',
            user=self.user
        )

        self.tag_1 = Tag.objects.create(name='test tag 1', user=self.user)
        self.tag_2 = Tag.objects.create(name='test tag 2', user=self.user)

    def test_retrieve_recipes_authorized(self):
        '''
        Test retrieving recipes by authorized user success
        '''

        Recipe.objects.create(title='recipe 1', user=self.user)
        Recipe.objects.create(title='recipe 2', user=self.user)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieving_recipes_limited_to_user(self):
        '''
        Test retrieving recipes by a user is limited to that user's recipes
        '''
        sampleUser = sample_user()
        Recipe.objects.create(
            title='recipe 1',
            user=sampleUser
        )

        recipe = Recipe.objects.create(
            title='recipe 2',
            user=self.user
        )

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], recipe.title)

    def test_retrieve_recipe_details_success(self):
        '''
        Test retrieving recipe details is successful
        '''
        recipe = Recipe.objects.create(
            title='recipe 1',
            user=self.user,
            price=1.00,
            time_minutes=1
        )
        recipe.tags.add(self.tag_1)
        recipe.ingredients.add(self.ingredient_1)

        url = recipe_detail_url(recipe)
        res = self.client.get(url)
        serialized = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized.data)

    def test_create_recipe_success(self):
        '''
        Test create recipe with valid information success
        '''
        payload = {
            'title': 'recipe 1',
            'price': 1.00,
            'time_minutes': 1,
        }

        res = self.client.post(RECIPE_URL, payload)
        exists = Recipe.objects.filter(
            title=payload['title'],
            price=payload['price'],
            time_minutes=payload['time_minutes'],
            user=self.user,
        ).exists()

        recipes = Recipe.objects.all()
        serialized = RecipeSerializer(recipes.first())

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(serialized.data, res.data)

    def test_create_recipe_with_no_title_fail(self):
        '''
        Test creating recipe with no title fail
        '''
        payload = {
            'title': '',
            'price': 1.00,
            'time_minutes': 1
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recipe_with_ingredient(self):
        '''
        Test creating recipe with ingredients success
        '''
        payload = {
            'title': 'recpie 1',
            'ingredients': [self.ingredient_1.id,
                            self.ingredient_2.id],
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(res.data['ingredients']), 2)
        self.assertEqual(res.data['ingredients'][0], payload['ingredients'][0])
    
    def test_create_recipe_with_tag(self):
        '''
        Test creating recipe with tags success
        '''
        payload = {
            'title': 'recpie 1',
            'tags': [self.tag_1.id,
                     self.tag_2.id],
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(res.data['tags']), 2)
        self.assertEqual(res.data['tags'][0], payload['tags'][0])


#############################################################################

    # def test_create_recipes_success(self):
    #     '''
    #     Test creating a recipe with authorized user is successful
    #     '''

    #     payload = {
    #         'name': 'recipe 1',
    #         'tags': 'test tag 1',
    #         'ingredients': ['test ingredient 1', 'test ingredient 2'],
    #     }
    #     res = self.client.post(RECIPE_URL, payload)

    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #     self.assertTrue(False)

    # def test_creating_invalid_recipe_fail(self):
    #     '''
    #     Test creating recipe with no name fail
    #     '''
    #     payload = {
    #         'name': ''
    #     }

    #     res = self.client.post(RECIPE_URL, payload)