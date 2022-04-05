import tempfile
import os
from PIL import Image
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


def recipe_image_url(recipe):
    return reverse('recipe:recipe-upload-image', args=[recipe.id])


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

    def test_patch_method_for_recpie(self):
        '''
        Test partially changing recpie attributes with patch method
        '''
        recipe = Recipe.objects.create(
            title='recpie 1',
            price=1.00,
            time_minutes=1,
            user=self.user
        )

        recipe.tags.add(self.tag_1)
        recipe.ingredients.add(self.ingredient_1)

        payload = {
            'title': 'recpie 1 editted',
            'time_minutes': 2,
            'tags': [self.tag_2.id],
            'ingredients': [self.ingredient_2.id]
        }

        url = recipe_detail_url(recipe)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key in payload.keys():

            self.assertEqual(res.data[key], payload[key])

    def test_put_method_for_recipe(self):
        '''
        Test whole changes with put method for recipes
        '''
        recipe = Recipe.objects.create(
            user=self.user,
            title='recipe 1',
        )
        payload = {
            'title': 'recipe 1 editted',
        }

        url = recipe_detail_url(recipe)
        res = self.client.put(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], payload['title'])


class RecipeImageTests(TestCase):
    '''
    Test recipe image field
    '''
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)
        self.recipe = Recipe.objects.create(
            title='test recipe',
            user=self.user
        )
    
    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_valid_image_success(self):
        '''
        Test uploading image with valid image success
        '''
        url = recipe_image_url(self.recipe)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)

            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_invalid_image_fail(self):
        '''
        Test uploading invalid image fail
        '''
        url = recipe_image_url(self.recipe)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_filtering_recipes_by_tags(self):
        '''
        Test filtering the recipes by the given tags comma separated ids
        '''

        recipe1 = Recipe.objects.create(title='recipe 1', user=self.user)
        recipe2 = Recipe.objects.create(title='recipe 2', user=self.user)
        recipe3 = Recipe.objects.create(title='recipe 3', user=self.user)

        tag1 = Tag.objects.create(name='tag 1', user=self.user)
        tag2 = Tag.objects.create(name='tag 1', user=self.user)

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        res = self.client.get(RECIPE_URL, 
            {'tags': f'{tag1.id},{tag2.id}'}
        )        
        
        recipe1_serialized = RecipeSerializer(recipe1)
        recipe2_serialized = RecipeSerializer(recipe2)
        recipe3_serialized = RecipeSerializer(recipe3)

        self.assertIn(recipe1_serialized.data, res.data)
        self.assertIn(recipe2_serialized.data, res.data)
        self.assertNotIn(recipe3_serialized.data, res.data)

    def test_filtering_recipes_by_ingredients(self):
        '''
        Test filtering the recipes by the given ingredients comma separated ids
        '''

        recipe1 = Recipe.objects.create(title='recipe 1', user=self.user)
        recipe2 = Recipe.objects.create(title='recipe 2', user=self.user)
        recipe3 = Recipe.objects.create(title='recipe 3', user=self.user)

        ingredient1 = Ingredient.objects.create(name='ingredient 1', user=self.user)
        ingredient2 = Ingredient.objects.create(name='ingredient 2', user=self.user)

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        res = self.client.get(RECIPE_URL, 
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        )        

        recipe1_serialized = RecipeSerializer(recipe1)
        recipe2_serialized = RecipeSerializer(recipe2)
        recipe3_serialized = RecipeSerializer(recipe3)

        self.assertIn(recipe1_serialized.data, res.data)
        self.assertIn(recipe2_serialized.data, res.data)
        self.assertNotIn(recipe3_serialized.data, res.data)