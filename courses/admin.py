from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.db import models
from .models import Category, Course, Lesson, Enrollment, Review, CourseProgress

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'price', 'difficulty', 'is_published', 'is_featured', 'students_enrolled', 'rating', 'created_at', 'video_preview']
    list_filter = ['is_published', 'is_featured', 'difficulty', 'category', 'created_at']
    search_fields = ['title', 'description', 'instructor__username', 'instructor__first_name', 'instructor__last_name']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['instructor', 'category']
    
    def get_search_results(self, request, queryset, search_term):
        """Custom search for autocomplete"""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset |= self.model.objects.filter(title__icontains=search_term)
        return queryset, use_distinct
    readonly_fields = ['students_enrolled', 'rating', 'total_ratings', 'created_at', 'updated_at', 'published_at', 'video_player']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'category', 'instructor')
        }),
        ('Course Details', {
            'fields': ('price', 'duration', 'difficulty', 'language')
        }),
        ('Media Content', {
            'fields': ('thumbnail', 'video_intro', 'course_video', 'video_player'),
            'description': 'Upload course thumbnail and videos. Course video will be displayed to students with access.'
        }),
        ('Content', {
            'fields': ('what_you_will_learn', 'requirements', 'target_audience')
        }),
        ('Status', {
            'fields': ('is_published', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('students_enrolled', 'rating', 'total_ratings'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['publish_courses', 'unpublish_courses', 'feature_courses', 'unfeature_courses']
    
    def video_preview(self, obj):
        """Show video preview in list view"""
        if obj.course_video:
            return format_html(
                '<span style="color: green;"><i class="fas fa-video"></i> Video</span>'
            )
        elif obj.video_intro:
            return format_html(
                '<span style="color: blue;"><i class="fab fa-youtube"></i> YouTube</span>'
            )
        return format_html('<span style="color: #999;">No Video</span>')
    video_preview.short_description = 'Video'
    
    def video_player(self, obj):
        """Display video player in detail view"""
        if obj.course_video:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<h4>Course Video Preview:</h4>'
                '<video controls style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
                '<source src="{}" type="video/mp4">'
                'Your browser does not support the video tag.'
                '</video>'
                '<br><br>'
                '<a href="{}" target="_blank" class="button" style="background: #007cba; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px;">'
                'View Video File'
                '</a>'
                '</div>',
                obj.course_video.url,
                obj.course_video.url
            )
        elif obj.video_intro:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<h4>Course Video (YouTube):</h4>'
                '<a href="{}" target="_blank" class="button" style="background: #ff0000; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px;">'
                '<i class="fab fa-youtube me-2"></i>Watch on YouTube'
                '</a>'
                '</div>',
                obj.video_intro
            )
        return format_html('<p style="color: #999; font-style: italic;">No video uploaded yet.</p>')
    video_player.short_description = 'Video Player'
    
    def publish_courses(self, request, queryset):
        queryset.update(is_published=True)
    publish_courses.short_description = "Publish selected courses"
    
    def unpublish_courses(self, request, queryset):
        queryset.update(is_published=False)
    unpublish_courses.short_description = "Unpublish selected courses"
    
    def feature_courses(self, request, queryset):
        queryset.update(is_featured=True)
    feature_courses.short_description = "Feature selected courses"
    
    def unfeature_courses(self, request, queryset):
        queryset.update(is_featured=False)
    unfeature_courses.short_description = "Unfeature selected courses"

class LessonAdminForm(forms.ModelForm):
    """Custom form for Lesson admin to ensure all courses are shown"""
    
    class Meta:
        model = Lesson
        fields = '__all__'
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all courses are shown in the dropdown, regardless of published status
        if 'course' in self.fields:
            # Get all courses and order them by title
            all_courses = Course.objects.all().order_by('title')
            self.fields['course'].queryset = all_courses
            
            # Add some debugging info
            print(f"Available courses in LessonAdminForm: {[c.title for c in all_courses]}")
            
            # Also print the current field choices
            choices = [(c.id, c.title) for c in all_courses]
            print(f"Course field choices: {choices}")
            self.fields['course'].choices = [('', '---------')] + choices

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    list_display = ['title', 'course', 'course_status', 'duration', 'order', 'is_free', 'video_preview', 'created_at']
    list_filter = ['is_free', 'course', 'created_at']
    search_fields = ['title', 'course__title']
    ordering = ['course', 'order']
    readonly_fields = ['video_player']
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'description', 'duration', 'order')
        }),
        ('Video Content', {
            'fields': ('video_url', 'video_file', 'video_player', 'is_free'),
            'description': 'Upload lesson video file or provide YouTube/Vimeo URL. Free lessons are accessible without payment.'
        }),
    )
    
    def video_preview(self, obj):
        """Show video preview in list view"""
        if obj.video_file:
            return format_html(
                '<span style="color: green;"><i class="fas fa-video"></i> File</span>'
            )
        elif obj.video_url:
            return format_html(
                '<span style="color: blue;"><i class="fab fa-youtube"></i> URL</span>'
            )
        return format_html('<span style="color: #999;">No Video</span>')
    video_preview.short_description = 'Video'
    
    def course_status(self, obj):
        """Show course published status"""
        if obj.course.is_published:
            return format_html('<span style="color: green;">✓ Published</span>')
        else:
            return format_html('<span style="color: orange;">⚠ Draft</span>')
    course_status.short_description = 'Course Status'
    
    def get_form(self, request, obj=None, **kwargs):
        """Override get_form to ensure our custom form is used"""
        form = super().get_form(request, obj, **kwargs)
        # Print available courses for debugging
        all_courses = Course.objects.all().order_by('title')
        print(f"Available courses in get_form: {[c.title for c in all_courses]}")
        return form
    
    def video_player(self, obj):
        """Display video player in detail view"""
        if obj.video_file:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<h4>Lesson Video Preview:</h4>'
                '<video controls style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
                '<source src="{}" type="video/mp4">'
                'Your browser does not support the video tag.'
                '</video>'
                '<br><br>'
                '<a href="{}" target="_blank" class="button" style="background: #007cba; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px;">'
                'View Video File'
                '</a>'
                '</div>',
                obj.video_file.url,
                obj.video_file.url
            )
        elif obj.video_url:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<h4>Lesson Video (External):</h4>'
                '<a href="{}" target="_blank" class="button" style="background: #007cba; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px;">'
                '<i class="fas fa-external-link-alt me-2"></i>Watch Video'
                '</a>'
                '</div>',
                obj.video_url
            )
        return format_html('<p style="color: #999; font-style: italic;">No video uploaded yet.</p>')
    video_player.short_description = 'Video Player'

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'completed_at', 'is_active']
    list_filter = ['is_active', 'enrolled_at', 'completed_at', 'course']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'course__title']
    readonly_fields = ['enrolled_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'rating', 'is_verified_purchase', 'is_helpful', 'is_moderated', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'is_helpful', 'is_moderated', 'created_at', 'course']
    search_fields = ['student__username', 'student__email', 'course__title', 'comment']
    readonly_fields = ['created_at', 'updated_at', 'helpful_count']
    list_editable = ['is_moderated', 'is_helpful']
    actions = ['approve_reviews', 'reject_reviews', 'mark_helpful', 'mark_unhelpful']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('student', 'course', 'rating', 'comment')
        }),
        ('Status', {
            'fields': ('is_verified_purchase', 'is_helpful', 'is_moderated', 'helpful_count')
        }),
        ('Moderation', {
            'fields': ('moderated_by', 'moderated_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def approve_reviews(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_moderated=True, moderated_by=request.user, moderated_at=timezone.now())
    approve_reviews.short_description = "Approve selected reviews"
    
    def reject_reviews(self, request, queryset):
        queryset.delete()
    reject_reviews.short_description = "Reject selected reviews"
    
    def mark_helpful(self, request, queryset):
        queryset.update(is_helpful=True)
    mark_helpful.short_description = "Mark selected reviews as helpful"
    
    def mark_unhelpful(self, request, queryset):
        queryset.update(is_helpful=False)
    mark_unhelpful.short_description = "Mark selected reviews as not helpful"

@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'completed', 'completed_at']
    list_filter = ['completed', 'completed_at', 'lesson__course']
    search_fields = ['student__username', 'lesson__title', 'lesson__course__title']
    readonly_fields = ['completed_at']
