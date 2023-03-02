"""
Database models.
"""

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, 
    PermissionsMixin, 
    BaseUserManager
)
# Create your models here.

class UserManager(BaseUserManager):
    # BaseUserManager provides a set of methods for managing users in a custom authentication system.
    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password):
        """Create and save a new superuser with given details"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        
        return user

class User(AbstractBaseUser, PermissionsMixin):
    # "AbstractBaseUser" is the most basic user model implementation and provides only the core implementation for a user model. 
    # You need to define all the fields and methods yourself to create a custom user model that extends AbstractBaseUser. 
    # For a class that provides more functionality, import AbstractUser instead.

    # "PermissionsMixin" provides a set of permissions-related methods and fields to a model
    "User model that supports using email instead of username"
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    # Defines the field we want to use for authentication as a username
    USERNAME_FIELD = 'email'
    
class Recipe(models.Model):
    """Recipe object"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    
    def __str__(self):
        return self.title
    
class Tag(models.Model):
    """Tag for filtering recipes"""
    name = models.CharField(max_length=255) 
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    def __str__(self):
        return self.name
    
class Ingredient(models.Model):
    """Ingredient for recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    def __str__(self):
        return self.name
    