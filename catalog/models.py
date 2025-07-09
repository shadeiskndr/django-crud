from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser
from movies.models import Movie


class UserMovieCatalog(models.Model):
    class Status(models.TextChoices):
        BOOKMARKED = 'bookmarked', 'Bookmarked'
        WATCHED = 'watched', 'Watched'
        WANT_TO_WATCH = 'want_to_watch', 'Want to Watch'
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='movie_catalog')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_catalog')
    status = models.CharField(max_length=20, choices=Status.choices)
    added_at = models.DateTimeField(auto_now_add=True)
    watched_at = models.DateTimeField(null=True, blank=True)
    personal_rating = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Personal rating from 0.0 to 10.0"
    )
    notes = models.TextField(blank=True, help_text="Personal notes about the movie")
    
    class Meta:
        unique_together = ['user', 'movie', 'status']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'added_at']),
            models.Index(fields=['movie', 'status']),
        ]
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.status})"


class UserMovieCollection(models.Model):
    """Custom movie collection created by users"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='movie_collections')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    movies = models.ManyToManyField(Movie, through='UserMovieCollectionItem', related_name='custom_collections')
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username}'s {self.name}"


class UserMovieCollectionItem(models.Model):
    """Through model for movies in custom collections"""
    movie_collection = models.ForeignKey(UserMovieCollection, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['movie_collection', 'movie']
        ordering = ['order', 'added_at']
