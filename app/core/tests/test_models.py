from django.test import TestCase
from django.contrib.auth import get_user_model

user = get_user_model()

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

			

     
		