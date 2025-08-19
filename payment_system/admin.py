from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import PaymentMethod, Payment, PaymentSettings

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_title', 'account_number', 'is_active', 'created_at']
    list_filter = ['name', 'is_active', 'created_at']
    search_fields = ['account_title', 'account_number']
    ordering = ['name']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'amount', 'payment_method', 'status', 'screenshot_verified', 'screenshot_preview', 'created_at']
    list_filter = ['status', 'screenshot_verified', 'payment_method', 'created_at']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'course__title', 'transaction_id', 'reference_number']
    readonly_fields = ['created_at', 'updated_at', 'verified_at', 'screenshot_display']
    actions = ['approve_payments', 'reject_payments', 'view_screenshots']
    list_per_page = 25
    
    class Media:
        css = {
            'all': ('admin/css/payment_admin.css',)
        }
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('student', 'course', 'payment_method', 'amount', 'transaction_id', 'reference_number')
        }),
        ('Screenshot Verification', {
            'fields': ('payment_screenshot', 'screenshot_display', 'screenshot_verified', 'verified_by', 'verified_at'),
            'description': 'Upload and verify the payment screenshot. The screenshot will be displayed below for easy verification.'
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes', 'student_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def screenshot_preview(self, obj):
        """Show a small preview of the screenshot in the list view"""
        if obj.payment_screenshot:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 4px;" />'
                '</a>',
                obj.payment_screenshot.url,
                obj.payment_screenshot.url
            )
        return format_html('<span style="color: #999;">No screenshot</span>')
    screenshot_preview.short_description = 'Screenshot'
    
    def screenshot_display(self, obj):
        """Display the screenshot in the detail view"""
        if obj.payment_screenshot:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<h4>Payment Screenshot:</h4>'
                '<div style="border: 1px solid #ddd; padding: 10px; border-radius: 8px; background: #f9f9f9;">'
                '<img src="{}" style="max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />'
                '<br><br>'
                '<a href="{}" target="_blank" class="button" style="background: #007cba; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px;">'
                'View Full Size'
                '</a>'
                '</div>'
                '</div>',
                obj.payment_screenshot.url,
                obj.payment_screenshot.url
            )
        return format_html('<p style="color: #999; font-style: italic;">No screenshot uploaded yet.</p>')
    screenshot_display.short_description = 'Screenshot Display'
    
    def approve_payments(self, request, queryset):
        for payment in queryset.filter(status='pending'):
            payment.approve_payment(request.user)
        self.message_user(request, f"Approved {queryset.filter(status='pending').count()} payments.")
    approve_payments.short_description = "Approve selected payments"
    
    def reject_payments(self, request, queryset):
        queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f"Rejected {queryset.filter(status='pending').count()} payments.")
    reject_payments.short_description = "Reject selected payments"
    
    def view_screenshots(self, request, queryset):
        """Custom action to view payment screenshots"""
        payments_with_screenshots = queryset.filter(payment_screenshot__isnull=False)
        if payments_with_screenshots:
            self.message_user(request, f"Found {payments_with_screenshots.count()} payments with screenshots. Click on individual payments to view screenshots.")
        else:
            self.message_user(request, "No payments with screenshots found in the selected items.")
    view_screenshots.short_description = "View payment screenshots"

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance
        return not PaymentSettings.objects.exists()
    
    fieldsets = (
        ('Platform Information', {
            'fields': ('platform_name', 'platform_email', 'platform_phone', 'platform_address')
        }),
        ('Support Information', {
            'fields': ('support_hours', 'whatsapp_number', 'payment_processing_time')
        }),
        ('EasyPaisa Account Details', {
            'fields': ('easypaisa_number', 'easypaisa_title'),
            'classes': ('collapse',)
        }),
        ('JazzCash Account Details', {
            'fields': ('jazzcash_number', 'jazzcash_title'),
            'classes': ('collapse',)
        }),
        ('Bank Account Details', {
            'fields': ('bank_account_number', 'bank_account_title', 'bank_name', 'bank_branch', 'bank_iban'),
            'classes': ('collapse',)
        }),
        ('Payment Instructions', {
            'fields': ('easypaisa_instructions', 'jazzcash_instructions', 'bank_transfer_instructions')
        }),
        ('Terms & Policies', {
            'fields': ('terms_conditions', 'refund_policy')
        }),
        ('Auto-Approval Settings', {
            'fields': ('auto_approve_payments', 'auto_approve_amount_limit')
        }),
        ('Notification Settings', {
            'fields': ('notify_admin_on_payment', 'notify_student_on_approval')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Make platform name readonly after creation
        if obj:
            return ('platform_name',)
        return ()
