from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Extends Django's default User model.
    """
    class Role(models.TextChoices):
        USER = 'USER', 'User'
        CRITIC = 'CRITIC', 'Critic'
        MODERATOR = 'MODERATOR', 'Moderator'
        ADMIN = 'ADMIN', 'Admin'

    email = models.EmailField(unique=True) # Make email the unique identifier
    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.USER
    )

    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # Still require username for createsuperuser

    def __str__(self):
        return self.email
