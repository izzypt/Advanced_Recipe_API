from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client 
# Client allows you to simulate requests to a Django application and get the responses. 
# An instance of the Client class allows you to make HTTP requests to the app being tested
# just like a real web browser would do. 
# You can then use the methods of the Client class to check the responses that are returned by the application.

class AdminSiteTests(TestCase):
    """Test dor Django admin site"""
    
    def setUp(self):
        # This method will run before every test. Allow us to setup
        """Create user and client."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='user@example.com',
            password='password123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='testUser@example.com',
            password='password123',
            name='Test User'
        )
    
    def test_users_list(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
        
    def test_edit_user_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, 200)
        
    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)




