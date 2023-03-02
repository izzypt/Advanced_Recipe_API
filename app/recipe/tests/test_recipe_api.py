"""
Tests for recipe APIs.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')

def create_user(**params):
    """Helper function to create new user"""
    return get_user_model().objects.create_user(**params)


def create_recipe(user, **params):
    """Helper function to create recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': Decimal('5.25'),
        'description': 'Sample recipe',
        'link': 'https://example.com/recipe.pdf',
    }
    defaults.update(params)
    
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

def detail_url(recipe_id):
    """Create and return a recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""
    
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(
            email='envkt@example.com',
            password='testpass'
        )
        self.client.force_authenticate(self.user)
        
    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user"""
        other_user = create_user(
            email='other_user@example.com',
            password='pass1234',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test retrieving a recipe detail"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload) # /api/recipes/recipe
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        original_link='https://example.com/recipe.pdf'
        recipe = create_recipe(user=self.user, title='Chocolate cheesecake', link=original_link)
        payload = {'title': 'New title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)
        
    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = create_recipe(
            user=self.user, 
            title='Chocolate cheesecake', 
            link='https://example.com/recipe.pdf',
            description="Sample recipe",
        )
        
        payload = {
            'title': 'New title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'Updated sample recipe',
            'time_minutes': 10,
            'price': Decimal('5.99'),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
        
    def test_update_user_returns_error(self):
        """Test that changing the recipe's user results in an error"""
        new_user = create_user(email='newuser', password='password')
        recipe = create_recipe(user=self.user)
        
        payload= {
            'user' : new_user.id
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        recipe = create_recipe(user=self.user)
        
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())
        
    def test_delete_other_users_recipe(self):
        """Test that we cannot delete another user's recipe"""
        new_user = create_user(email='newuser', password='password')
        recipe = create_recipe(user=new_user)
        
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())


    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'tags': [{'name': 'Vegan'}, {'name': 'Dessert'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)
              
    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tags"""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)


    def test_create_tag_on_update(self):
        """Test creating a new tag when updating a recipe"""
        recipe = create_recipe(user=self.user)

        payload = {'tags': [{'name': 'Breakfast'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe"""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tags."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)
        
        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients"""
        payload ={
            'title': 'CheeseCake',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'ingredients':[{'name': 'Cheese'}, {'name': 'Butter'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'], 
                user=self.user
            ).exists()

    def test_create_recipe_with_existing_ingredients(self):
        """Test creating a new recipe with existing ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name='Cheese')
        payload = {
            'title': 'CheeseCake',
            'time_minutes': 30,
            'price': Decimal('2.99'),
            'Ingredients': [{'name': 'Cheese'}, {'name': 'Butter'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'], 
                user=self.user

            ).exists()
            self.assertTrue(exists)
