from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm, UserRegistrationForm

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # UserProfile is automatically created by the signal in models.py
            
            # Log the user in
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, f'Welcome {username}! Your account has been created successfully.')
            return redirect('courses:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def dashboard(request):
    """User dashboard"""
    # Get user's enrolled courses
    enrollments = request.user.enrollments.filter(is_active=True).order_by('-enrolled_at')
    
    # Get user's recent payments
    payments = request.user.payments.all().order_by('-created_at')[:5]
    
    # Get user's recent reviews
    reviews = request.user.reviews.all().order_by('-created_at')[:5]
    
    context = {
        'enrollments': enrollments,
        'payments': payments,
        'reviews': reviews,
    }
    return render(request, 'accounts/dashboard.html', context)
