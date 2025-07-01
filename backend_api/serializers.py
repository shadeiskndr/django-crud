from rest_framework import serializers
from .models import Movie

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class MovieListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'original_title', 'release_date', 
            'vote_average', 'vote_count', 'popularity', 'poster_path',
            'genres_names', 'overview', 'runtime'
        ]

class MovieCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for create/update operations with validation"""
    class Meta:
        model = Movie
        exclude = ('created_at', 'updated_at')
        
    def validate_vote_average(self, value):
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("Vote average must be between 0 and 10")
        return value
    
    def validate_runtime(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Runtime cannot be negative")
        return value
