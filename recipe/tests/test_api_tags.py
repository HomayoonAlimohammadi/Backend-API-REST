from django.test import TestCase
from core.models import Recipe, Tag
from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsTests(TestCase):

    def setUp(self):
        '''
        Set up client and authenticate
        '''
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='test123',
            name='test name'
        )
    
    def test_retrieve_tags_list(self):
        '''
        Test to retrieve all tags list
        '''
        Tag.objects.create(user=self.user, name='tag1')

        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsTests(TestCase):

    def setUp(self):
        '''
        Set up authenticated user
        '''
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@test.com', 
            password='test123',
            name='test user'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_tags_authenticated(self):
        '''
        Test retrieving tags by authenticated user
        '''
        Tag.objects.create(user=self.user, name='tag1')
        Tag.objects.create(user=self.user, name='tag2')

        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)
        
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_specific_tags(self):
        '''
        Test retrieving user specific tags
        '''
        user = get_user_model().objects.create_user(
            email='user@test.com',
            password='test123',
            name='test name'
            )
        Tag.objects.create(user=user, name='test tag')
        
        tag = Tag.objects.create(user=self.user, name='tag')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        '''
        Test creating tags success
        '''
        payload = {
            'name': 'tag1'
        }

        res = self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            name=payload['name'],
            user=self.user,
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_invalid_tags_fail(self):
        '''
        Test creating invalid tags fail
        '''
        payload = {
            'name': ''
        }

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_tags_duplicate_name_by_user_fail(self):
        '''
        Test creating tags with duplicate name by the same user fail
        '''
        Tag.objects.create(
            name='tag1',
            user=self.user
        )

        payload = {
            'name': 'tag1'
        }

        with self.assertRaises(ValueError):
            self.client.post(TAGS_URL, payload)

    def test_return_assinged_tags_only(self):
        '''
        Test returning assigned only tags and nothing more
        '''

        tag1 = Tag.objects.create(name='tag1', user=self.user)
        tag2 = Tag.objects.create(name='tag2', user=self.user)

        recipe = Recipe.objects.create(
            title='recipe1', 
            user=self.user,
            price=5.00,
            time_minutes=3
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        tag1_serialized = TagSerializer(tag1)
        tag2_serialized = TagSerializer(tag2)

        self.assertIn(tag1_serialized.data, res.data)
        self.assertNotIn(tag2_serialized.data, res.data)

    def test_return_unique_tags(self):
        '''
        Test not returning multiple tags for the same instance
        '''

        tag = Tag.objects.create(name='tag1', user=self.user)
        Tag.objects.create(name='tag2', user=self.user)

        recipe1 = Recipe.objects.create(
            title='recipe1', 
            user=self.user,
            price=5.00,
            time_minutes=3
        )
        recipe2 = Recipe.objects.create(
            title='recipe2', 
            user=self.user,
            price=5.00,
            time_minutes=3
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)