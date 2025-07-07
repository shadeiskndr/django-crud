from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import CustomUser
from backend_api.models import Movie


class Review(models.Model):
    """User reviews for movies"""
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        HIDDEN = 'HIDDEN', 'Hidden'  # Hidden by moderators
        DELETED = 'DELETED', 'Deleted'  # Soft delete
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=200, help_text="Review title/headline")
    content = models.TextField(help_text="Review content")
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Rating from 0.0 to 10.0"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Moderation fields
    is_featured = models.BooleanField(default=False, help_text="Featured by moderators")
    moderated_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='moderated_reviews'
    )
    moderation_notes = models.TextField(blank=True, help_text="Internal moderation notes")
    
    # Analytics
    helpful_count = models.PositiveIntegerField(default=0)
    reported_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'movie']  # One review per user per movie
        indexes = [
            models.Index(fields=['movie', 'status', '-published_at']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', '-helpful_count']),
            models.Index(fields=['is_featured', 'status']),
        ]
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s review of {self.movie.title}"
    
    def save(self, *args, **kwargs):
        # Auto-set published_at when status changes to PUBLISHED
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class ReviewVote(models.Model):
    """Users can vote reviews as helpful or not helpful"""
    class VoteType(models.TextChoices):
        HELPFUL = 'HELPFUL', 'Helpful'
        NOT_HELPFUL = 'NOT_HELPFUL', 'Not Helpful'
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='review_votes')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=20, choices=VoteType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'review']  # One vote per user per review
        indexes = [
            models.Index(fields=['review', 'vote_type']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} voted {self.vote_type} on {self.review}"


class ReviewReport(models.Model):
    """Users can report inappropriate reviews"""
    class ReportReason(models.TextChoices):
        SPAM = 'SPAM', 'Spam'
        INAPPROPRIATE = 'INAPPROPRIATE', 'Inappropriate Content'
        SPOILERS = 'SPOILERS', 'Contains Spoilers'
        OFF_TOPIC = 'OFF_TOPIC', 'Off Topic'
        HARASSMENT = 'HARASSMENT', 'Harassment'
        OTHER = 'OTHER', 'Other'
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='review_reports')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=ReportReason.choices)
    description = models.TextField(blank=True, help_text="Additional details")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Moderation
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_reports'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'review']  # One report per user per review
        indexes = [
            models.Index(fields=['resolved', 'created_at']),
            models.Index(fields=['review', 'resolved']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report by {self.user.username} for {self.review}"