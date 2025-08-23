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

class GlobalDiscount(models.Model):
    """Global discount for all courses"""
    title = models.CharField(max_length=200, default="Limited Time Offer!")
    description = models.CharField(max_length=300, default="Get amazing discounts on all AI courses")
    discount_percentage = models.PositiveIntegerField(help_text="Discount percentage (e.g., 50 for 50% off)")
    
    # Timing
    start_date = models.DateTimeField(null=True, blank=True, help_text="When the discount starts (leave blank for immediate start)")
    end_date = models.DateTimeField(help_text="When the discount expires")
    
    # Status
    is_active = models.BooleanField(default=False, help_text="Whether the global discount is currently active")
    
    # Display settings
    show_banner = models.BooleanField(default=True, help_text="Show the discount banner on pages")
    banner_color = models.CharField(max_length=20, default="orange", choices=[
        ('orange', 'Orange'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('purple', 'Purple'),
    ])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Global Discount"
        verbose_name_plural = "Global Discounts"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.discount_percentage}% off"
    
    def is_currently_active(self):
        """Check if the global discount is currently active"""
        if not self.is_active:
            return False
        
        now = timezone.now()
        return (self.start_date is None or now >= self.start_date) and now <= self.end_date
    
    def get_remaining_time(self):
        """Get remaining time in seconds"""
        if not self.is_currently_active():
            return 0
        
        now = timezone.now()
        remaining = self.end_date - now
        return max(0, int(remaining.total_seconds()))
    
    def get_discount_multiplier(self):
        """Get the discount multiplier (e.g., 0.5 for 50% off)"""
        from decimal import Decimal
        return Decimal(str((100 - self.discount_percentage) / 100))
    
    def apply_to_price(self, original_price):
        """Apply discount to a price"""
        if not self.is_currently_active():
            return original_price
        
        return original_price * self.get_discount_multiplier()
    
    def save(self, *args, **kwargs):
        # Update active status based on current time
        self.is_active = self.is_currently_active()
        super().save(*args, **kwargs)

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
    
    # Discount fields
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                                       help_text="Discounted price during promotion")
    discount_start_date = models.DateTimeField(null=True, blank=True, 
                                             help_text="When the discount starts")
    discount_end_date = models.DateTimeField(null=True, blank=True, 
                                           help_text="When the discount ends")
    is_discount_active = models.BooleanField(default=False, 
                                           help_text="Whether the discount is currently active")
    
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
    
    def has_active_discount(self):
        """Check if course has an active individual discount"""
        if not self.is_discount_active or not self.discount_price or not self.discount_end_date:
            return False
        
        now = timezone.now()
        return (self.discount_start_date is None or now >= self.discount_start_date) and now <= self.discount_end_date
    
    def has_any_discount(self):
        """Check if course has any active discount (individual or global)"""
        # Check individual discount first
        if self.has_active_discount():
            return True
        
        # Check global discount
        from .models import GlobalDiscount
        global_discount = GlobalDiscount.objects.filter(is_active=True).first()
        return global_discount and global_discount.is_currently_active()
    
    def get_current_price(self):
        """Get the current price (discounted if active, otherwise regular price)"""
        # Check for individual course discount first
        if self.has_active_discount():
            return self.discount_price
        
        # Check for global discount
        from .models import GlobalDiscount
        global_discount = GlobalDiscount.objects.filter(is_active=True).first()
        if global_discount and global_discount.is_currently_active():
            return global_discount.apply_to_price(self.price)
        
        return self.price
    
    def get_discount_percentage(self):
        """Calculate discount percentage"""
        # Check for individual course discount first
        if self.has_active_discount():
            if self.price == 0:
                return 0
            
            discount_amount = self.price - self.discount_price
            percentage = (discount_amount / self.price) * 100
            return round(percentage, 0)
        
        # Check for global discount
        from .models import GlobalDiscount
        global_discount = GlobalDiscount.objects.filter(is_active=True).first()
        if global_discount and global_discount.is_currently_active():
            return global_discount.discount_percentage
        
        return 0
    
    def get_discount_remaining_time(self):
        """Get remaining time for discount in seconds"""
        if not self.has_active_discount():
            return 0
        
        now = timezone.now()
        remaining = self.discount_end_date - now
        return max(0, int(remaining.total_seconds()))
    
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
        
        # Update discount active status
        if self.discount_price and self.discount_end_date:
            self.is_discount_active = self.has_active_discount()
        
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

class SiteSettings(models.Model):
    """Site-wide settings for branding and configuration"""
    site_name = models.CharField(max_length=100, default="AI Course Platform", help_text="Main site name")
    site_tagline = models.CharField(max_length=200, default="Learn AI & Machine Learning", help_text="Site tagline/subtitle")
    logo = models.ImageField(upload_to='site_logos/', null=True, blank=True, help_text="Site logo (recommended: 200x50px)")
    favicon = models.ImageField(upload_to='site_favicons/', null=True, blank=True, help_text="Favicon (recommended: 32x32px)")
    footer_text = models.TextField(default="© 2024 AI Course Platform. All rights reserved.", help_text="Footer copyright text")
    contact_email = models.EmailField(default="contact@aicourseplatform.com", help_text="Contact email address")
    contact_phone = models.CharField(max_length=20, default="+1 (555) 123-4567", help_text="Contact phone number")
    
    # Social Media Links
    facebook_url = models.URLField(blank=True, null=True, help_text="Facebook page URL")
    twitter_url = models.URLField(blank=True, null=True, help_text="Twitter/X page URL")
    linkedin_url = models.URLField(blank=True, null=True, help_text="LinkedIn page URL")
    instagram_url = models.URLField(blank=True, null=True, help_text="Instagram page URL")
    youtube_url = models.URLField(blank=True, null=True, help_text="YouTube channel URL")
    
    # SEO Settings
    meta_description = models.TextField(default="Learn AI and Machine Learning with our comprehensive online courses. Expert-led tutorials, hands-on projects, and flexible learning paths.", help_text="Meta description for SEO")
    meta_keywords = models.CharField(max_length=500, default="AI, Machine Learning, Python, Data Science, Online Courses", help_text="Meta keywords for SEO")
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True, null=True, help_text="Google Analytics tracking ID (GA4)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return f"Site Settings - {self.site_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            return
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get the site settings, create if doesn't exist"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'AI Course Platform',
                'site_tagline': 'Learn AI & Machine Learning',
                'footer_text': '© 2024 AI Course Platform. All rights reserved.',
                'contact_email': 'contact@aicourseplatform.com',
                'contact_phone': '+1 (555) 123-4567',
                'meta_description': 'Learn AI and Machine Learning with our comprehensive online courses. Expert-led tutorials, hands-on projects, and flexible learning paths.',
                'meta_keywords': 'AI, Machine Learning, Python, Data Science, Online Courses',
            }
        )
        return settings

class Banner(models.Model):
    """Dynamic banner management for hero section"""
    
    title = models.CharField(max_length=200, help_text="Banner title")
    subtitle = models.CharField(max_length=300, blank=True, help_text="Banner subtitle")
    description = models.TextField(blank=True, help_text="Banner description")
    image = models.ImageField(upload_to='banners/', help_text="Banner image (recommended: 1920x600px)")
    mobile_image = models.ImageField(upload_to='banners/mobile/', blank=True, null=True, help_text="Mobile optimized image (optional)")
    
    # Animation settings
    animation_type = models.CharField(
        max_length=50,
        choices=[
            ('fade', 'Fade In/Out'),
            ('slide', 'Slide Left/Right'),
            ('zoom', 'Zoom In/Out'),
            ('bounce', 'Bounce'),
            ('flip', 'Flip'),
        ],
        default='fade',
        help_text="Animation effect for this banner"
    )
    
    # Display settings
    banner_type = models.CharField(max_length=20, default='hero', editable=False)
    is_active = models.BooleanField(default=True, help_text="Show this banner")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers first)")
    
    # Timing settings
    start_date = models.DateTimeField(blank=True, null=True, help_text="When to start showing this banner")
    end_date = models.DateTimeField(blank=True, null=True, help_text="When to stop showing this banner")
    
    # Call to action
    cta_text = models.CharField(max_length=100, blank=True, help_text="Call to action button text")
    cta_url = models.CharField(max_length=200, blank=True, help_text="Call to action URL")
    cta_color = models.CharField(
        max_length=20,
        choices=[
            ('primary', 'Primary Blue'),
            ('secondary', 'Secondary Gray'),
            ('success', 'Success Green'),
            ('danger', 'Danger Red'),
            ('warning', 'Warning Yellow'),
            ('info', 'Info Cyan'),
            ('light', 'Light White'),
            ('dark', 'Dark Black'),
        ],
        default='primary',
        help_text="Button color"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
    
    def __str__(self):
        return f"{self.title} (Hero Banner)"
    
    def is_currently_active(self):
        """Check if banner should be displayed now"""
        if not self.is_active:
            return False
        
        now = timezone.now()
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def get_image_url(self, request=None):
        """Get appropriate image URL based on device"""
        if request and hasattr(request, 'META'):
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
                if self.mobile_image:
                    return self.mobile_image.url
        
        return self.image.url
    
    def get_animation_class(self):
        """Get CSS animation class"""
        animation_classes = {
            'fade': 'animate__animated animate__fadeIn',
            'slide': 'animate__animated animate__slideInLeft',
            'zoom': 'animate__animated animate__zoomIn',
            'bounce': 'animate__animated animate__bounceIn',
            'flip': 'animate__animated animate__flipInX',
        }
        return animation_classes.get(self.animation_type, 'animate__animated animate__fadeIn')
