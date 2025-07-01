from django.contrib import admin
from .models import Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'release_date', 'vote_average', 
        'popularity', 'runtime', 'created_at'
    ]
    list_filter = [
        'adult', 'video', 'release_date', 'original_language'
    ]
    search_fields = ['title', 'original_title', 'overview']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'original_title', 'overview', 'tagline', 'homepage')
        }),
        ('Release Information', {
            'fields': ('release_date', 'status', 'original_language', 'adult', 'video')
        }),
        ('Ratings & Popularity', {
            'fields': ('vote_average', 'vote_count', 'popularity')
        }),
        ('Financial', {
            'fields': ('budget', 'revenue', 'runtime')
        }),
        ('Media', {
            'fields': ('poster_path', 'backdrop_path')
        }),
        ('Categories', {
            'fields': ('genres', 'genres_names')
        }),
        ('Production', {
            'fields': (
                'production_companies', 'production_companies_names',
                'production_countries', 'production_countries_names',
                'spoken_languages', 'spoken_languages_names'
            )
        }),
        ('External IDs', {
            'fields': (
                'imdb_id', 'external_imdb_id', 'external_twitter_id',
                'external_facebook_id', 'external_wikidata_id', 'external_instagram_id'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
