from rest_framework import serializers
from django.utils import timezone
from django.db import IntegrityError
from .models import Review, ReviewVote, ReviewReport
from backend_api.serializers import MovieListSerializer
from users.serializers import UserSerializer
from backend_api.models import Movie


class ReviewSerializer(serializers.ModelSerializer):
    """Full review serializer with nested data"""
    user = UserSerializer(read_only=True)
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    user_vote = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_moderate = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'movie', 'movie_id', 'title', 'content', 'rating',
            'status', 'created_at', 'updated_at', 'published_at', 'is_featured',
            'helpful_count', 'reported_count', 'user_vote', 'can_edit', 'can_moderate'
        ]
        read_only_fields = ['user', 'published_at', 'helpful_count', 'reported_count']
    
    def get_user_vote(self, obj):
        """Get current user's vote on this review"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            return vote.vote_type if vote else None
        return None
    
    def get_can_edit(self, obj):
        """Check if current user can edit this review"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False
    
    def get_can_moderate(self, obj):
        """Check if current user can moderate this review"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from users.models import CustomUser
            return request.user.role in [CustomUser.Role.MODERATOR, CustomUser.Role.ADMIN]
        return False
    
    def validate_movie_id(self, value):
        """Validate that the movie exists"""
        try:
            Movie.objects.get(id=value)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie not found.")
        return value
    
    def create(self, validated_data):
        """Create review with automatic user assignment"""
        movie_id = validated_data.pop('movie_id')
        movie = Movie.objects.get(id=movie_id)
        user = self.context['request'].user
        
        try:
            review = Review.objects.create(
                user=user,
                movie=movie,
                **validated_data
            )
            return review
        except IntegrityError:
            raise serializers.ValidationError(
                "You have already reviewed this movie."
            )


class ReviewCreateUpdateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating/updating reviews"""
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = ['title', 'content', 'rating', 'status', 'movie_id']
    
    def validate_movie_id(self, value):
        try:
            Movie.objects.get(id=value)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie not found.")
        return value
       
    def create(self, validated_data):
        """Create review with automatic user assignment"""
        movie_id = validated_data.pop('movie_id')
        movie = Movie.objects.get(id=movie_id)
        user = validated_data.pop('user')
        
        # Check if user already has a review for this movie
        if Review.objects.filter(user=user, movie=movie).exists():
            raise serializers.ValidationError(
                "You have already reviewed this movie."
            )
        
        review = Review.objects.create(
            user=user,
            movie=movie,
            **validated_data
        )
        return review


class ReviewListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for review lists"""
    user = serializers.StringRelatedField()
    movie = serializers.StringRelatedField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'movie', 'title', 'rating', 'status',
            'published_at', 'is_featured', 'helpful_count'
        ]


class ReviewVoteSerializer(serializers.ModelSerializer):
    """Serializer for review votes"""
    review_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ReviewVote
        fields = ['id', 'user', 'review_id', 'vote_type', 'created_at']
        read_only_fields = ['user']
    
    def validate_review_id(self, value):
        try:
            review = Review.objects.get(id=value)
            # Can't vote on your own review
            if review.user == self.context['request'].user:
                raise serializers.ValidationError("You cannot vote on your own review.")
            # Can only vote on published reviews
            if review.status != Review.Status.PUBLISHED:
                raise serializers.ValidationError("You can only vote on published reviews.")
        except Review.DoesNotExist:
            raise serializers.ValidationError("Review not found.")
        return value
    
    def create(self, validated_data):
        review_id = validated_data.pop('review_id')
        review = Review.objects.get(id=review_id)
        user = validated_data.pop('user')

        # Update or create vote
        vote, created = ReviewVote.objects.update_or_create(
            user=user,
            review=review,
            defaults={'vote_type': validated_data['vote_type']}
        )
        
        # Update helpful_count on review
        self._update_helpful_count(review)
        return vote
    
    def _update_helpful_count(self, review):
        """Update the helpful count on the review"""
        helpful_votes = review.votes.filter(vote_type=ReviewVote.VoteType.HELPFUL).count()
        review.helpful_count = helpful_votes
        review.save(update_fields=['helpful_count'])


class ReviewReportSerializer(serializers.ModelSerializer):
    """Serializer for reporting reviews"""
    review_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ReviewReport
        fields = [
            'id', 'user', 'review_id', 'reason', 'description', 
            'created_at', 'resolved', 'resolved_at'
        ]
        read_only_fields = ['user', 'resolved', 'resolved_at']
    
    def validate_review_id(self, value):
        try:
            review = Review.objects.get(id=value)
            # Can't report your own review
            if review.user == self.context['request'].user:
                raise serializers.ValidationError("You cannot report your own review.")
        except Review.DoesNotExist:
            raise serializers.ValidationError("Review not found.")
        return value
    
    def create(self, validated_data):
        review_id = validated_data.pop('review_id')
        review = Review.objects.get(id=review_id)
        user = validated_data.pop('user') 
        
        try:
            report = ReviewReport.objects.create(
                user=user,
                review=review,
                **validated_data
            )
            
            # Update reported_count on review
            review.reported_count = review.reports.count()
            review.save(update_fields=['reported_count'])
            
            return report
        except IntegrityError:
            raise serializers.ValidationError(
                "You have already reported this review."
            )


class ModerationSerializer(serializers.ModelSerializer):
    """Serializer for moderation actions"""
    
    class Meta:
        model = Review
        fields = ['id', 'status', 'is_featured', 'moderation_notes']
    
    def update(self, instance, validated_data):
        # Set moderated_by to current user
        validated_data['moderated_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class ReportResolutionSerializer(serializers.ModelSerializer):
    """Serializer for resolving reports"""
    
    class Meta:
        model = ReviewReport
        fields = ['id', 'resolved', 'resolution_notes']
    
    def update(self, instance, validated_data):
        if validated_data.get('resolved', False) and not instance.resolved:
            validated_data['resolved_by'] = self.context['request'].user
            validated_data['resolved_at'] = timezone.now()
        return super().update(instance, validated_data)