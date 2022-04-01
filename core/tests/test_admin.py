from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class TestAdmin(TestCase):

    def setUp(self):
        '''
        Setting up admin and additional user
        '''
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@test.com',
            password='test123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@test.com',
            password='test123',
            name='Test user full name'
        )

    def test_admin_user_list(self):
        '''
        Testing admin user list
        '''
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_admin_user_change(self):
        '''
        Testing admin site user change view
        '''
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
    
    def test_admin_user_add(self):
        '''
        Testing admin site user creation page
        '''
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
