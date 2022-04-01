from django.test import TestCase
from core.models import Tag
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
