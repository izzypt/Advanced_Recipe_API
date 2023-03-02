"""
Tests for the ingredients API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')

def create_user(email='user@example.com', password='testpass'):
    """Create a new user"""
    return get_user_model().objects.create_user(email, password)

def detail_url(ingredient_id):
    """Return the detail URL for the ingredient"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])

class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated ingredients API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class privateIngredientsApiTests(TestCase):
    """Test authenticated ingredients API access"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')
        
        # Make request
        res = self.client.get(INGREDIENT_URL)
        
        # Get the ingredients from the DB
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        
        # Check that the ingredients we saved are equal to the ones we retrieved
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_ingredients_limited_to_user(self):
        """Test that list of ingredients is limited to the authenticated user"""
        
        # Create a second user
        user2 = create_user(email='upchh@example.com', password='testpass')
        
        # Create an ingredient for both users
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Tumeric')
        
        # Make request         
        res = self.client.get(INGREDIENT_URL)

        # Check we only got 1 ingredient for the user
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient_successful(self):
        """Test updating a ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Vinegar')

        payload = {'name': 'Cabbage'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient_successful(self):
        """Test deleting a ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Vinegar')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

