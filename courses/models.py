from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models import Avg
import os

def validate_video_file(value):
    """Validate video file upload"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.mp4', '.webm', '.avi', '.mov', '.mkv']
    
    if ext not in valid_extensions:
        raise ValidationError('Unsupported video format. Please upload MP4, WebM, AVI, MOV, or MKV files.')
    
    # Check file size (500MB limit)
    if value.size > 524288000:  # 500MB in bytes
        raise ValidationError('Video file size must be under 500MB.')

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    
    # Course details
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, help_text="e.g., '10 hours', '5 weeks'")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    language = models.CharField(max_length=50, default='English')
    
    # Media
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    video_intro = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    course_video = models.FileField(upload_to='course_videos/', blank=True, null=True, 
                                   help_text="Upload course introduction video (MP4, WebM, AVI, MOV, MKV - Max 500MB)",
                                   validators=[validate_video_file])
    
    # Content
    what_you_will_learn = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    target_audience = models.TextField(blank=True)
    
    # Stats
    students_enrolled = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.PositiveIntegerField(default=0)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('courses:course_detail', kwargs={'slug': self.slug})
    
    def is_free(self):
        """Check if course is free"""
        return self.price == 0
    
    def user_has_access(self, user):
        """Check if user has access to this course"""
        if not user.is_authenticated:
            return False
        
        # Free courses are accessible to everyone
        if self.is_free():
            return True
        
        # Check if user has approved payment
        from payment_system.models import Payment
        approved_payment = Payment.objects.filter(
            student=user,
            course=self,
            status='approved'
        ).exists()
        
        return approved_payment
    
    def user_is_enrolled(self, user):
        """Check if user is enrolled in this course"""
        if not user.is_authenticated:
            return False
        
        return self.enrollments.filter(student=user, is_active=True).exists()
    
    def get_rating_distribution(self):
        """Get rating distribution for analytics"""
        from django.db.models import Count
        distribution = self.reviews.filter(is_moderated=True).values('rating').annotate(
            count=Count('rating')
        ).order_by('rating')
        
        # Create a complete distribution (1-5 stars)
        complete_distribution = {}
        for i in range(1, 6):
            complete_distribution[i] = 0
        
        for item in distribution:
            complete_distribution[item['rating']] = item['count']
        
        return complete_distribution
    
    def get_rating_percentage(self, rating):
        """Get percentage of a specific rating"""
        total_reviews = self.reviews.filter(is_moderated=True).count()
        if total_reviews == 0:
            return 0
        
        rating_count = self.reviews.filter(is_moderated=True, rating=rating).count()
        return round((rating_count / total_reviews) * 100, 1)
    
    def get_recent_reviews(self, limit=5):
        """Get recent reviews"""
        return self.reviews.filter(is_moderated=True).order_by('-created_at')[:limit]
    
    def get_verified_reviews(self):
        """Get reviews from verified purchases"""
        return self.reviews.filter(is_moderated=True, is_verified_purchase=True)
    
    def get_helpful_reviews(self):
        """Get reviews marked as helpful"""
        return self.reviews.filter(is_moderated=True, is_helpful=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug is unique
            counter = 1
            original_slug = self.slug
            while Course.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    video_file = models.FileField(upload_to='lesson_videos/', blank=True, null=True,
                                 help_text="Upload lesson video file (MP4, WebM, AVI, MOV, MKV - Max 500MB)",
                                 validators=[validate_video_file])
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    order = models.PositiveIntegerField(default=0)
    is_free = models.BooleanField(default=False, help_text="Free lessons are accessible without payment")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def get_video_source(self):
        """Get the video source (URL or file)"""
        if self.video_file:
            return self.video_file.url
        elif self.video_url:
            return self.video_url
        return None
    
    def has_video(self):
        """Check if lesson has video content"""
        return bool(self.video_file or self.video_url)
    
    def user_has_access(self, user):
        """Check if user has access to this lesson"""
        if not user.is_authenticated:
            return False
        
        # Free lessons are accessible to everyone
        if self.is_free:
            return True
        
        # Check if user has access to the course
        return self.course.user_has_access(user)
    
    def get_previous_by_order(self):
        """Get the previous lesson in the course"""
        try:
            return self.course.lessons.filter(order__lt=self.order).order_by('-order').first()
        except:
            return None
    
    def get_next_by_order(self):
        """Get the next lesson in the course"""
        try:
            return self.course.lessons.filter(order__gt=self.order).order_by('order').first()
        except:
            return None

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    
    # Additional feedback fields
    helpful_count = models.PositiveIntegerField(default=0)
    helpful_votes = models.ManyToManyField(User, related_name='helpful_reviews', blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    is_helpful = models.BooleanField(default=False)
    is_moderated = models.BooleanField(default=True)
    moderated_at = models.DateTimeField(blank=True, null=True)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_reviews')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.rating} stars"
    
    def get_rating_display_text(self):
        """Get the text representation of the rating"""
        rating_texts = {
            1: 'Poor',
            2: 'Fair', 
            3: 'Good',
            4: 'Very Good',
            5: 'Excellent'
        }
        return rating_texts.get(self.rating, 'Unknown')
    
    def get_stars_display(self):
        """Get HTML for star display"""
        stars = ''
        for i in range(1, 6):
            if i <= self.rating:
                stars += '<i class="fas fa-star text-warning"></i>'
            else:
                stars += '<i class="far fa-star text-muted"></i>'
        return stars
    
    def save(self, *args, **kwargs):
        # Check if this is a verified purchase
        if not self.is_verified_purchase:
            from payment_system.models import Payment
            self.is_verified_purchase = Payment.objects.filter(
                student=self.student,
                course=self.course,
                status='approved'
            ).exists()
        
        super().save(*args, **kwargs)
        
        # Update course rating statistics
        self.update_course_rating()
    
    def update_course_rating(self):
        """Update course rating statistics"""
        reviews = self.course.reviews.filter(is_moderated=True)
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            self.course.rating = round(avg_rating, 2)
            self.course.total_ratings = reviews.count()
        else:
            self.course.rating = 0.00
            self.course.total_ratings = 0
        self.course.save()

class CourseProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['student', 'lesson']
    
    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"
