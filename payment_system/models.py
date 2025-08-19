from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from courses.models import Course

class PaymentMethod(models.Model):
    PAYMENT_CHOICES = [
        ('easypaisa', 'EasyPaisa'),
        ('jazzcash', 'JazzCash'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=50, choices=PAYMENT_CHOICES)
    account_number = models.CharField(max_length=100, blank=True)
    account_title = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.account_title}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, help_text="Transaction ID from payment provider")
    reference_number = models.CharField(max_length=100, blank=True, help_text="Reference number provided by student")
    
    # Screenshot verification
    payment_screenshot = models.ImageField(upload_to='payment_screenshots/', blank=True, null=True)
    screenshot_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    verified_at = models.DateTimeField(blank=True, null=True)
    
    # Status and notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Notes from admin")
    student_notes = models.TextField(blank=True, help_text="Notes from student")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.amount}"
    
    def approve_payment(self, admin_user):
        """Approve the payment and enroll the student"""
        self.status = 'approved'
        self.screenshot_verified = True
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.save()
        
        # Create enrollment
        from courses.models import Enrollment
        enrollment, created = Enrollment.objects.get_or_create(
            student=self.student,
            course=self.course,
            defaults={'is_active': True}
        )
        
        # Update course enrollment count
        self.course.students_enrolled += 1
        self.course.save()
    
    def reject_payment(self, admin_user, notes=""):
        """Reject the payment"""
        self.status = 'rejected'
        self.admin_notes = notes
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.save()

class PaymentSettings(models.Model):
    """Global payment settings"""
    platform_name = models.CharField(max_length=100, default="AI Course Platform")
    platform_email = models.EmailField(default="admin@aicourseplatform.com")
    platform_phone = models.CharField(max_length=20, default="+92 300 1234567")
    platform_address = models.TextField(blank=True, help_text="Platform address for bank transfers")
    
    # Payment instructions
    easypaisa_instructions = models.TextField(blank=True, help_text="Step-by-step instructions for EasyPaisa payments")
    jazzcash_instructions = models.TextField(blank=True, help_text="Step-by-step instructions for JazzCash payments")
    bank_transfer_instructions = models.TextField(blank=True, help_text="Step-by-step instructions for bank transfers")
    
    # Payment account details (can be overridden by PaymentMethod)
    easypaisa_number = models.CharField(max_length=20, blank=True, help_text="EasyPaisa account number")
    easypaisa_title = models.CharField(max_length=100, blank=True, help_text="EasyPaisa account title")
    jazzcash_number = models.CharField(max_length=20, blank=True, help_text="JazzCash account number")
    jazzcash_title = models.CharField(max_length=100, blank=True, help_text="JazzCash account title")
    bank_account_number = models.CharField(max_length=50, blank=True, help_text="Bank account number")
    bank_account_title = models.CharField(max_length=100, blank=True, help_text="Bank account title")
    bank_name = models.CharField(max_length=100, blank=True, help_text="Bank name")
    bank_branch = models.CharField(max_length=100, blank=True, help_text="Bank branch")
    bank_iban = models.CharField(max_length=50, blank=True, help_text="Bank IBAN (if applicable)")
    
    # Auto-approval settings
    auto_approve_payments = models.BooleanField(default=False, help_text="Automatically approve payments below the limit")
    auto_approve_amount_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Maximum amount for auto-approval")
    
    # Notification settings
    notify_admin_on_payment = models.BooleanField(default=True, help_text="Send email notification to admin on new payment")
    notify_student_on_approval = models.BooleanField(default=True, help_text="Send email notification to student on payment approval")
    
    # Additional settings
    payment_processing_time = models.CharField(max_length=50, default="24-48 hours", help_text="Expected payment processing time")
    refund_policy = models.TextField(blank=True, help_text="Refund policy information")
    terms_conditions = models.TextField(blank=True, help_text="Payment terms and conditions")
    
    # Support information
    support_hours = models.CharField(max_length=100, default="24/7 Available", help_text="Support hours")
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="WhatsApp support number")
    
    class Meta:
        verbose_name_plural = "Payment Settings"
    
    def __str__(self):
        return "Payment Settings"
    
    @classmethod
    def get_settings(cls):
        """Get or create payment settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
