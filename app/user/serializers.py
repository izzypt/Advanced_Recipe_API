"""
Serializers for the user API view.
"""
from django.contrib.auth import (
    get_user_model, 
    authenticate
    )

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        # extra_kwargs allows us to provide extra metadata to the different fields.
        # We set password to write_only and a minimum length of 5 characters.
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # crete() allows us to override the serializer's default behavior when we create a new object out of the serializer.
    # default behaviour is to create an object with all values passed in.
    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)
    # update() is overriding the update() method of the serializer.
    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user
    
class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    
    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = ('unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs
            