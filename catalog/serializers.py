from rest_framework import serializers
from django.db import IntegrityError
from .models import UserMovieCatalog, MovieList, MovieListItem
from backend_api.serializers import MovieListSerializer
from backend_api.models import Movie


class UserMovieCatalogSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserMovieCatalog
        fields = [
            'id', 'movie', 'movie_id', 'status', 'added_at', 
            'watched_at', 'personal_rating', 'notes'
        ]
        read_only_fields = ['added_at']
    
    def validate_movie_id(self, value):
        if not Movie.objects.filter(id=value).exists():
            raise serializers.ValidationError("Movie with this ID does not exist.")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CatalogActionSerializer(serializers.Serializer):
    """Simple serializer for quick catalog actions"""
    movie_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)
    personal_rating = serializers.FloatField(
        required=False, 
        min_value=0.0, 
        max_value=10.0
    )
    
    def validate_movie_id(self, value):
        if not Movie.objects.filter(id=value).exists():
            raise serializers.ValidationError("Movie with this ID does not exist.")
        return value


class MovieListItemSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    
    class Meta:
        model = MovieListItem
        fields = ['movie', 'added_at', 'order']


class MovieListSerializer(serializers.ModelSerializer):
    movies = MovieListItemSerializer(source='movielistitem_set', many=True, read_only=True)
    movie_count = serializers.SerializerMethodField()
    owner = serializers.StringRelatedField(source='user', read_only=True)
    
    class Meta:
        model = MovieList
        fields = [
            'id', 'name', 'description', 'is_public', 'created_at', 
            'updated_at', 'movies', 'movie_count', 'owner'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_movie_count(self, obj):
        return obj.movies.count()
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MovieListCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating lists"""
    class Meta:
        model = MovieList
        fields = ['id', 'name', 'description', 'is_public']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                'name': 'A list with this name already exists.'
            })
    
    def validate_name(self, value):
        """Check for duplicate names for the current user"""
        user = self.context['request'].user
        if MovieList.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError('A list with this name already exists.')
        return value


class AddToListSerializer(serializers.Serializer):
    """Serializer for adding movies to lists"""
    movie_id = serializers.IntegerField()
    
    def validate_movie_id(self, value):
        if not Movie.objects.filter(id=value).exists():
            raise serializers.ValidationError("Movie with this ID does not exist.")
        return value
