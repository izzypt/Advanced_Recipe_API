"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models

user = get_user_model()

def create_user(email='envkt@example.com', password='testpass'):
	"""Create and return a new user"""
	return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

	def test_create_user_with_email_successful(self):
		email = 'test@example.com'
		password = 'testpass123'
		user = get_user_model().objects.create_user(
			email=email, 
			password=password,
		)
  
		self.assertEqual(user.email, email)
		self.assertTrue(user.check_password(password))
  
	def test_new_user_email_normalized(self):
		sample_emails = [
			['anpch@EXAMPle.com', 'anpch@example.com'],
			['efpyi@ExamplE.com', 'efpyi@example.com'],
   			['test3@EXAMPLE.COM', 'test3@example.com'],
      		['test4@example.COM', 'test4@example.com']
    	]
		for email, expected_email in sample_emails:
			user = get_user_model().objects.create_user(email, 'test123')
			self.assertEqual(user.email, expected_email)
   
	def test_new_user_without_email_raises_error(self):
		with self.assertRaises(ValueError):
			get_user_model().objects.create_user(None, 'test123')
   
	def test_create_superuser(self):
		"""Test creating a new superuser"""
		user = get_user_model().objects.create_superuser(
			'teste@example.com',
			'test123'
		)
		self.assertTrue(user.is_superuser)
		self.assertTrue(user.is_staff)

			
	def test_create_recipe(self):
		"""Test creating a recipe is sucessful."""
		user = get_user_model().objects.create_user(
			'teste@example.com',
   			'testpass123'
		)
		recipe = models.Recipe.objects.create(
			user = user,
			title = 'Sample recipe name',
			time_minutes = 5,
			price=Decimal('5.50'),
			description = 'Sample recipe description'

		)
		self.assertEqual(str(recipe), recipe.title)

	def test_create_tag(self):
		"""Test creating a tag is sucessful."""
		user = create_user()
		tag = models.Tag.objects.create(user=user, name='Vegan')

		self.assertEqual(str(tag), tag.name)
  
	def test_create_ingredient(self):
		"""Test creating an ingredient is sucessful."""
		user = create_user()
		ingredient = models.Ingredient.objects.create(user=user, name='Cucumber')

		self.assertEqual(str(ingredient), ingredient.name)
		