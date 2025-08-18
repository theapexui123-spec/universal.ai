from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Payment, PaymentMethod, PaymentSettings
from courses.models import Course, Enrollment
from django.db.models import Q

@login_required
def payment_page(request, slug):
    """Payment page for course purchase"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('course_detail', slug=slug)
    
    # Check if payment already exists
    existing_payment = Payment.objects.filter(
        student=request.user,
        course=course,
        status='pending'
    ).first()
    
    if existing_payment:
        messages.info(request, 'You have a pending payment for this course.')
        return redirect('payment_detail', payment_id=existing_payment.id)
    
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    payment_settings = PaymentSettings.get_settings()
    
    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id', '')
        reference_number = request.POST.get('reference_number', '')
        student_notes = request.POST.get('student_notes', '')
        
        if payment_method_id:
            payment_method = get_object_or_404(PaymentMethod, id=payment_method_id)
            
            # Create payment record
            payment = Payment.objects.create(
                student=request.user,
                course=course,
                payment_method=payment_method,
                amount=course.price,
                transaction_id=transaction_id,
                reference_number=reference_number,
                student_notes=student_notes,
                status='pending'
            )
            
            messages.success(request, 'Payment submitted successfully! Please upload your payment screenshot.')
            return redirect('payment_detail', payment_id=payment.id)
        else:
            messages.error(request, 'Please select a payment method.')
    
    context = {
        'course': course,
        'payment_methods': payment_methods,
        'payment_settings': payment_settings,
    }
    return render(request, 'payment_system/payment_page.html', context)

@login_required
def payment_detail(request, payment_id):
    """Payment detail page with screenshot upload"""
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    
    if request.method == 'POST':
        payment_screenshot = request.FILES.get('payment_screenshot')
        
        if payment_screenshot:
            payment.payment_screenshot = payment_screenshot
            payment.save()
            messages.success(request, 'Payment screenshot uploaded successfully! Admin will verify it soon.')
            return redirect('payment_status', payment_id=payment.id)
        else:
            messages.error(request, 'Please upload a payment screenshot.')
    
    context = {
        'payment': payment,
    }
    return render(request, 'payment_system/payment_detail.html', context)

@login_required
def payment_status(request, payment_id):
    """Payment status page"""
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    
    context = {
        'payment': payment,
    }
    return render(request, 'payment_system/payment_status.html', context)

@login_required
def my_payments(request):
    """User's payment history"""
    payments = Payment.objects.filter(student=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(payments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'payment_system/my_payments.html', context)

@staff_member_required
def admin_payments(request):
    """Admin view for managing payments"""
    payments = Payment.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Filter by payment method
    method_filter = request.GET.get('method')
    if method_filter:
        payments = payments.filter(payment_method__name=method_filter)
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        payments = payments.filter(
            Q(student__username__icontains=search_query) |
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(course__title__icontains=search_query) |
            Q(transaction_id__icontains=search_query) |
            Q(reference_number__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get payment methods for filter
    payment_methods = PaymentMethod.objects.all()
    
    context = {
        'page_obj': page_obj,
        'payment_methods': payment_methods,
        'current_status': status_filter,
        'current_method': method_filter,
        'search_query': search_query,
    }
    return render(request, 'payment_system/admin_payments.html', context)

@staff_member_required
@require_POST
def approve_payment(request, payment_id):
    """Approve a payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status == 'pending':
        payment.approve_payment(request.user)
        messages.success(request, f'Payment for {payment.course.title} has been approved.')
    else:
        messages.error(request, 'Payment cannot be approved.')
    
    return redirect('admin_payments')

@staff_member_required
@require_POST
def reject_payment(request, payment_id):
    """Reject a payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    notes = request.POST.get('notes', '')
    
    if payment.status == 'pending':
        payment.reject_payment(request.user, notes)
        messages.success(request, f'Payment for {payment.course.title} has been rejected.')
    else:
        messages.error(request, 'Payment cannot be rejected.')
    
    return redirect('admin_payments')

@staff_member_required
def payment_methods_admin(request):
    """Admin view for managing payment methods"""
    payment_methods = PaymentMethod.objects.all().order_by('name')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        account_title = request.POST.get('account_title')
        account_number = request.POST.get('account_number')
        
        if name and account_title:
            PaymentMethod.objects.create(
                name=name,
                account_title=account_title,
                account_number=account_number
            )
            messages.success(request, 'Payment method added successfully.')
            return redirect('payment_methods_admin')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'payment_methods': payment_methods,
    }
    return render(request, 'payment_system/payment_methods_admin.html', context)

@staff_member_required
@require_POST
def toggle_payment_method(request, method_id):
    """Toggle payment method active status"""
    payment_method = get_object_or_404(PaymentMethod, id=method_id)
    payment_method.is_active = not payment_method.is_active
    payment_method.save()
    
    status = 'activated' if payment_method.is_active else 'deactivated'
    messages.success(request, f'Payment method {status} successfully.')
    
    return redirect('payment_methods_admin')

def payment_instructions(request):
    """Payment instructions page"""
    payment_settings = PaymentSettings.get_settings()
    
    context = {
        'payment_settings': payment_settings,
    }
    return render(request, 'payment_system/payment_instructions.html', context)
