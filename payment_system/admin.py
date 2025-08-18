from django.contrib import admin
from .models import PaymentMethod, Payment, PaymentSettings

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_title', 'account_number', 'is_active', 'created_at']
    list_filter = ['name', 'is_active', 'created_at']
    search_fields = ['account_title', 'account_number']
    ordering = ['name']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'amount', 'payment_method', 'status', 'screenshot_verified', 'created_at']
    list_filter = ['status', 'screenshot_verified', 'payment_method', 'created_at']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'course__title', 'transaction_id', 'reference_number']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']
    actions = ['approve_payments', 'reject_payments']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('student', 'course', 'payment_method', 'amount', 'transaction_id', 'reference_number')
        }),
        ('Screenshot Verification', {
            'fields': ('payment_screenshot', 'screenshot_verified', 'verified_by', 'verified_at')
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes', 'student_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def approve_payments(self, request, queryset):
        for payment in queryset.filter(status='pending'):
            payment.approve_payment(request.user)
        self.message_user(request, f"Approved {queryset.filter(status='pending').count()} payments.")
    approve_payments.short_description = "Approve selected payments"
    
    def reject_payments(self, request, queryset):
        queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f"Rejected {queryset.filter(status='pending').count()} payments.")
    reject_payments.short_description = "Reject selected payments"

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance
        return not PaymentSettings.objects.exists()
    
    fieldsets = (
        ('Platform Information', {
            'fields': ('platform_name', 'platform_email', 'platform_phone')
        }),
        ('Payment Instructions', {
            'fields': ('easypaisa_instructions', 'jazzcash_instructions', 'bank_transfer_instructions')
        }),
        ('Auto-Approval Settings', {
            'fields': ('auto_approve_payments', 'auto_approve_amount_limit')
        }),
        ('Notification Settings', {
            'fields': ('notify_admin_on_payment', 'notify_student_on_approval')
        }),
    )
