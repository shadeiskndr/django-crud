from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the CustomUser model (for reading user data)."""
    # Make role read-only to prevent users from changing it via a general update endpoint
    role = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        # We don't include 'role' here as an input field.
        # It will be set by the model's default value.
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        # The 'role' will be automatically set to the default 'USER'
        # by the model when create_user is called.
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user
