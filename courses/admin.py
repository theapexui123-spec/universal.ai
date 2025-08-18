from django.contrib import admin
from .models import Category, Course, Lesson, Enrollment, Review, CourseProgress

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'price', 'difficulty', 'is_published', 'is_featured', 'students_enrolled', 'rating', 'created_at']
    list_filter = ['is_published', 'is_featured', 'difficulty', 'category', 'created_at']
    search_fields = ['title', 'description', 'instructor__username', 'instructor__first_name', 'instructor__last_name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['students_enrolled', 'rating', 'total_ratings', 'created_at', 'updated_at', 'published_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'category', 'instructor')
        }),
        ('Course Details', {
            'fields': ('price', 'duration', 'difficulty', 'language')
        }),
        ('Media', {
            'fields': ('thumbnail', 'video_intro')
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

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'duration', 'order', 'is_free', 'created_at']
    list_filter = ['is_free', 'course', 'created_at']
    search_fields = ['title', 'course__title']
    ordering = ['course', 'order']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'completed_at', 'is_active']
    list_filter = ['is_active', 'enrolled_at', 'completed_at', 'course']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'course__title']
    readonly_fields = ['enrolled_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'course']
    search_fields = ['student__username', 'course__title', 'comment']
    readonly_fields = ['created_at']

@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'completed', 'completed_at']
    list_filter = ['completed', 'completed_at', 'lesson__course']
    search_fields = ['student__username', 'lesson__title', 'lesson__course__title']
    readonly_fields = ['completed_at']
