from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Movie(models.Model):
    # Basic movie info
    # id is automatically created by Django as PRIMARY KEY
    adult = models.BooleanField(default=False)
    title = models.TextField()
    original_title = models.TextField()
    video = models.BooleanField(default=False)
    budget = models.BigIntegerField(null=True, blank=True)
    revenue = models.BigIntegerField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    status = models.TextField(blank=True)
    imdb_id = models.TextField(blank=True)
    tagline = models.TextField(blank=True)
    homepage = models.URLField(blank=True, max_length=500)
    overview = models.TextField(blank=True)
    popularity = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)
    vote_average = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    release_date = models.DateField(null=True, blank=True)
    original_language = models.CharField(max_length=10, blank=True)
    poster_path = models.TextField(blank=True)
    backdrop_path = models.TextField(blank=True)
    
    # Flattened arrays/objects (stored as JSON strings)
    genres = models.JSONField(null=True, blank=True)  # JSON array of genre objects
    genres_names = models.TextField(blank=True)  # Comma-separated genre names
    origin_country = models.JSONField(null=True, blank=True)  # JSON array
    spoken_languages = models.JSONField(null=True, blank=True)  # JSON array
    spoken_languages_names = models.TextField(blank=True)  # Comma-separated language names
    production_companies = models.JSONField(null=True, blank=True)  # JSON array
    production_companies_names = models.TextField(blank=True)  # Comma-separated company names
    production_countries = models.JSONField(null=True, blank=True)  # JSON array
    production_countries_names = models.TextField(blank=True)  # Comma-separated country names
    
    # Collection info (flattened)
    collection_id = models.IntegerField(null=True, blank=True)
    collection_name = models.TextField(blank=True)
    collection_poster_path = models.TextField(blank=True)
    collection_backdrop_path = models.TextField(blank=True)
    
    # External IDs (flattened)
    external_imdb_id = models.TextField(blank=True)
    external_twitter_id = models.TextField(blank=True)
    external_facebook_id = models.TextField(blank=True)
    external_wikidata_id = models.TextField(blank=True)
    external_instagram_id = models.TextField(blank=True)
    
    # Videos (stored as JSON)
    videos = models.JSONField(null=True, blank=True)
    
    # Django conveniences
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['release_date']),
            models.Index(fields=['vote_average']),
            models.Index(fields=['popularity']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else 'Unknown'})"
