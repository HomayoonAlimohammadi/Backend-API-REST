# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APIClient
# from core.models import Recipe, Ingredient, Tag
# from recipe.serializers import RecipeSerializer


# RECIPE_URL = reverse('recipe:list')


# def sample_user(email='sample@test.com',
#                 password='sample123',
#                 name='sample name'):
#     return get_user_model().objects.create_user(
#         email=email,
#         password=password,
#         name=name
#     )


# class PublicRecipeAPITests(TestCase):
#     '''
#     Tests for public api recipe
#     '''
    
#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user(
#             email='test@test.com',
#             password='test123',
#             name='test user'
#         )

#     def test_retrieve_recipe_unauthorized(self):
#         '''
#         Test retrieving recipes unauthorized fail
#         '''
#         Recipe.objects.create(
#             name='recipe 1',
#             user=self.user,
#         )

#         res = self.client.get(RECIPE_URL)

#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# class PrivateRecipeAPITests(TestCase):

#     def setUp(self):
#         self.user = get_user_model().objects.create_user(
#             name='test user',
#             email='test@test.com',
#             password='test123'
#         )

#         self.client = APIClient()
#         self.client.force_authenticate(self.user)
#         self.ingredient_1 = Ingredient.objects.create(
#             name='test ingredient 1',
#             user=self.user
#         )
#         self.ingredient_2 = Ingredient.objects.create(
#             name='test ingredient 2',
#             user=self.user
#         )
#         self.tag_1 = Tag.objects.create(
#             name='test tag 1',
#             user=self.user
#         )
#         self.tag_2 = Tag.objects.create(
#             name='test tag 2',
#             user=self.user,
#         )

#     def test_retrieve_recipes_authorized(self):
#         '''
#         Test retrieving recipes by authorized user success
#         '''

#         recipe = Recipe.objects.create(
#             name='recipe 1',
#             user=self.user
#         )

#         recipe.tags.add(self.tag_1)
#         recipe.ingredients.add(self.ingredient_1)

#         res = self.client.get(RECIPE_URL)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(res.data), 1)

#     def test_recipe_string(self):
#         '''
#         Test string representation of recipes is their name
#         '''
#         recipe = Recipe.objects.create(
#             name='recipe 1',
#             user=self.user,
#         )

#         self.assertEqual(str(recipe), recipe.name)

# #############################################################################


#     # def test_create_recipes_success(self):
#     #     '''
#     #     Test creating a recipe with authorized user is successful
#     #     '''

#     #     payload = {
#     #         'name': 'recipe 1',
#     #         'tags': 'test tag 1',
#     #         'ingredients': ['test ingredient 1', 'test ingredient 2'],
#     #     }
#     #     res = self.client.post(RECIPE_URL, payload)

#     #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#     #     self.assertTrue(False)

#     # def test_creating_invalid_recipe_fail(self):
#     #     '''
#     #     Test creating recipe with no name fail
#     #     '''
#     #     payload = {
#     #         'name': ''
#     #     }

#     #     res = self.client.post(RECIPE_URL, payload)