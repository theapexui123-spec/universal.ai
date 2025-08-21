from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Review, Course
from django.db import models

class ReviewForm(forms.ModelForm):
    """Enhanced review form with better validation and UI"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(
                attrs={
                    'id': 'rating-hidden'
                }
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Share your experience with this course...',
                    'id': 'comment-textarea'
                }
            )
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        
        # Customize rating choices
        self.fields['rating'].choices = [
            ('', 'Select rating'),
            (5, '⭐⭐⭐⭐⭐ Excellent'),
            (4, '⭐⭐⭐⭐ Very Good'),
            (3, '⭐⭐⭐ Good'),
            (2, '⭐⭐ Fair'),
            (1, '⭐ Poor'),
        ]
        
        # Add validation attributes
        self.fields['rating'].required = True
        self.fields['comment'].required = True
    
    def clean_comment(self):
        """Validate comment content"""
        comment = self.cleaned_data.get('comment')
        
        if comment:
            # Check minimum length
            if len(comment.strip()) < 10:
                raise ValidationError('Review must be at least 10 characters long.')
            
            # Check maximum length
            if len(comment) > 1000:
                raise ValidationError('Review cannot exceed 1000 characters.')
            
            # Check for inappropriate content (basic check)
            inappropriate_words = ['spam', 'advertisement', 'promotion']
            comment_lower = comment.lower()
            for word in inappropriate_words:
                if word in comment_lower:
                    raise ValidationError('Review contains inappropriate content.')
        
        return comment
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        
        # Check if user has already reviewed this course
        if self.user and self.course:
            existing_review = Review.objects.filter(
                student=self.user,
                course=self.course
            ).first()
            
            if existing_review and not self.instance.pk:
                raise ValidationError('You have already reviewed this course.')
        
        return cleaned_data

class ReviewFilterForm(forms.Form):
    """Form for filtering reviews"""
    
    RATING_CHOICES = [
        ('', 'All Ratings'),
        ('5', '5 Stars'),
        ('4', '4 Stars'),
        ('3', '3 Stars'),
        ('2', '2 Stars'),
        ('1', '1 Star'),
    ]
    
    SORT_CHOICES = [
        ('newest', 'Newest First'),
        ('oldest', 'Oldest First'),
        ('highest', 'Highest Rating'),
        ('lowest', 'Lowest Rating'),
        ('helpful', 'Most Helpful'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='newest',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    verified_only = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    helpful_only = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class CourseRatingForm(forms.Form):
    """Form for course rating analytics"""
    
    def __init__(self, course, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.course = course
    
    def get_rating_stats(self):
        """Get comprehensive rating statistics"""
        reviews = self.course.reviews.filter(is_moderated=True)
        
        if not reviews.exists():
            return {
                'total_reviews': 0,
                'average_rating': 0,
                'rating_distribution': {},
                'verified_reviews': 0,
                'helpful_reviews': 0,
            }
        
        # Basic stats
        total_reviews = reviews.count()
        average_rating = reviews.aggregate(avg=models.Avg('rating'))['avg']
        
        # Rating distribution
        distribution = self.course.get_rating_distribution()
        
        # Additional stats
        verified_reviews = reviews.filter(is_verified_purchase=True).count()
        helpful_reviews = reviews.filter(is_helpful=True).count()
        
        return {
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 2) if average_rating else 0,
            'rating_distribution': distribution,
            'verified_reviews': verified_reviews,
            'helpful_reviews': helpful_reviews,
        }
