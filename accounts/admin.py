from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone_number']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'address', 'bio', 'profile_picture')
        }),
        ('Social Media', {
            'fields': ('website', 'linkedin', 'twitter', 'github'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'sms_notifications'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
