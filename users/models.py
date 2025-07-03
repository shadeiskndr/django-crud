from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Extends Django's default User model.
    You can add more fields here in the future.
    """
    email = models.EmailField(unique=True) # Make email the unique identifier

    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # Still require username for createsuperuser

    def __str__(self):
        return self.email
