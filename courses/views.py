from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from .models import Course, Category, Enrollment, Review, CourseProgress, Lesson, Banner
from .forms import ReviewForm, ReviewFilterForm, CourseRatingForm
from payment_system.models import Payment, PaymentMethod, PaymentSettings

def home(request):
    """Landing page with featured courses"""
    featured_courses = Course.objects.filter(is_published=True, is_featured=True)[:6]
    latest_courses = Course.objects.filter(is_published=True).order_by('-created_at')[:6]
    categories = Category.objects.all()[:8]
    
    # Get top reviews for testimonials section
    top_reviews = Review.objects.filter(
        is_moderated=True,
        rating__gte=4
    ).order_by('-created_at')[:6]
    
    # Get active banners for hero section
    active_banners = Banner.objects.filter(
        is_active=True
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=timezone.now())
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
    ).order_by('order', '-created_at')
    
    context = {
        'featured_courses': featured_courses,
        'latest_courses': latest_courses,
        'categories': categories,
        'active_banners': active_banners,
        'top_reviews': top_reviews,
    }
    return render(request, 'courses/home.html', context)

def course_list(request):
    """List all published courses with filtering and search"""
    courses = Course.objects.filter(is_published=True)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(instructor__first_name__icontains=query) |
            Q(instructor__last_name__icontains=query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        courses = courses.filter(category_id=category_id)
    
    # Difficulty filter
    difficulty = request.GET.get('difficulty')
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    
    # Price filter
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        courses = courses.filter(price__gte=price_min)
    if price_max:
        courses = courses.filter(price__lte=price_max)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price_low':
        courses = courses.order_by('price')
    elif sort_by == 'price_high':
        courses = courses.order_by('-price')
    elif sort_by == 'rating':
        courses = courses.order_by('-rating')
    elif sort_by == 'students':
        courses = courses.order_by('-students_enrolled')
    else:
        courses = courses.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'current_difficulty': difficulty,
        'current_sort': sort_by,
        'query': query,
    }
    return render(request, 'courses/course_list.html', context)

def course_detail(request, slug):
    """Course detail page"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Check user access and enrollment status
    user_has_access = False
    is_enrolled = False
    payment_status = None
    
    if request.user.is_authenticated:
        user_has_access = course.user_has_access(request.user)
        is_enrolled = course.user_is_enrolled(request.user)
        
        # Check payment status
        from payment_system.models import Payment
        payment = Payment.objects.filter(
            student=request.user,
            course=course
        ).order_by('-created_at').first()
        
        if payment:
            payment_status = payment.status
    
    # Get lessons
    lessons = course.lessons.all()
    
    # Get reviews with filtering
    review_filter_form = ReviewFilterForm(request.GET)
    reviews = course.reviews.filter(is_moderated=True)
    
    # Apply filters
    if review_filter_form.is_valid():
        rating = review_filter_form.cleaned_data.get('rating')
        sort_by = review_filter_form.cleaned_data.get('sort_by', 'newest')
        verified_only = review_filter_form.cleaned_data.get('verified_only')
        helpful_only = review_filter_form.cleaned_data.get('helpful_only')
        
        if rating:
            reviews = reviews.filter(rating=rating)
        if verified_only:
            reviews = reviews.filter(is_verified_purchase=True)
        if helpful_only:
            reviews = reviews.filter(is_helpful=True)
        
        # Apply sorting
        if sort_by == 'oldest':
            reviews = reviews.order_by('created_at')
        elif sort_by == 'highest':
            reviews = reviews.order_by('-rating', '-created_at')
        elif sort_by == 'lowest':
            reviews = reviews.order_by('rating', '-created_at')
        elif sort_by == 'helpful':
            reviews = reviews.order_by('-helpful_count', '-created_at')
        else:  # newest
            reviews = reviews.order_by('-created_at')
    
    # Paginate reviews
    review_paginator = Paginator(reviews, 10)
    review_page = request.GET.get('review_page')
    review_page_obj = review_paginator.get_page(review_page)
    
    # Get rating statistics
    rating_form = CourseRatingForm(course)
    rating_stats = rating_form.get_rating_stats()
    
    # Calculate rating distribution with percentages for template
    rating_distribution_with_percentages = {}
    for rating in range(1, 6):
        count = rating_stats['rating_distribution'].get(rating, 0)
        percentage = course.get_rating_percentage(rating)
        rating_distribution_with_percentages[rating] = {
            'count': count,
            'percentage': percentage
        }
    
    # Get related courses
    related_courses = Course.objects.filter(
        category=course.category,
        is_published=True
    ).exclude(id=course.id)[:4]
    
    # Get payment methods
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    context = {
        'course': course,
        'lessons': lessons,
        'reviews': review_page_obj,
        'review_filter_form': review_filter_form,
        'rating_stats': rating_stats,
        'rating_distribution_with_percentages': rating_distribution_with_percentages,
        'related_courses': related_courses,
        'user_has_access': user_has_access,
        'is_enrolled': is_enrolled,
        'payment_status': payment_status,
        'payment_methods': payment_methods,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def course_enroll(request, slug):
    """Enroll in a course"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('course_detail', slug=slug)
    
    # Create enrollment
    enrollment = Enrollment.objects.create(
        student=request.user,
        course=course,
        is_active=True
    )
    
    # Update course enrollment count
    course.students_enrolled += 1
    course.save()
    
    messages.success(request, f'Successfully enrolled in {course.title}!')
    return redirect('course_detail', slug=slug)

@login_required
def course_learn(request, slug):
    """Course learning page"""
    course = get_object_or_404(Course, slug=slug)
    
    # Check if user has access to this course
    if not course.user_has_access(request.user):
        if course.is_free():
            messages.error(request, 'You need to be logged in to access this course.')
        else:
            messages.error(request, 'You need to purchase this course to access its content.')
        return redirect('courses:course_detail', slug=slug)
    
    # Check if user is enrolled, if not create enrollment
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'is_active': True}
    )
    
    if created:
        # Update course enrollment count
        course.students_enrolled += 1
        course.save()
    
    # Get all lessons
    lessons = course.lessons.all()
    
    # Get progress for each lesson
    lesson_progress = {}
    completed_lessons = 0
    total_lessons = lessons.count()
    
    for lesson in lessons:
        progress, created = CourseProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson,
            defaults={'completed': False}
        )
        lesson_progress[lesson.id] = progress
        if progress.completed:
            completed_lessons += 1
    
    # Calculate progress percentage
    progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'lessons': lessons,
        'lesson_progress': lesson_progress,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'progress_percentage': round(progress_percentage, 1),
    }
    return render(request, 'courses/course_learn.html', context)

@login_required
def lesson_detail(request, slug, lesson_id):
    """Individual lesson page"""
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    # Check if user has access to this lesson
    if not lesson.user_has_access(request.user):
        if lesson.is_free:
            messages.error(request, 'You need to be logged in to access this lesson.')
        else:
            messages.error(request, 'You need to purchase this course to access this lesson.')
        return redirect('courses:course_detail', slug=slug)
    
    # Check if user is enrolled, if not create enrollment
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'is_active': True}
    )
    
    if created:
        # Update course enrollment count
        course.students_enrolled += 1
        course.save()
    
    # Get or create progress for this lesson
    progress, created = CourseProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson,
        defaults={'completed': False}
    )
    
    # Get all lessons and calculate overall progress
    lessons = course.lessons.all()
    completed_lessons = 0
    total_lessons = lessons.count()
    
    for course_lesson in lessons:
        lesson_progress, created = CourseProgress.objects.get_or_create(
            student=request.user,
            lesson=course_lesson,
            defaults={'completed': False}
        )
        if lesson_progress.completed:
            completed_lessons += 1
    
    # Calculate progress percentage
    progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    # Get next and previous lessons
    lessons_list = list(lessons)
    current_index = lessons_list.index(lesson)
    next_lesson = lessons_list[current_index + 1] if current_index < len(lessons_list) - 1 else None
    prev_lesson = lessons_list[current_index - 1] if current_index > 0 else None
    
    context = {
        'course': course,
        'lesson': lesson,
        'current_lesson': lesson,
        'progress': progress,
        'lesson_completed': progress.completed,
        'next_lesson': next_lesson,
        'prev_lesson': prev_lesson,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'progress_percentage': round(progress_percentage, 1),
    }
    return render(request, 'courses/lesson_detail.html', context)

@login_required
@require_POST
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as complete"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Check if user is enrolled in the course
    if not Enrollment.objects.filter(student=request.user, course=lesson.course, is_active=True).exists():
        return JsonResponse({'error': 'Not enrolled in this course'}, status=403)
    
    progress, created = CourseProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson,
        defaults={'completed': False}
    )
    
    if not progress.completed:
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
    
    return JsonResponse({'success': True})

@login_required
def my_courses(request):
    """User's enrolled courses"""
    enrollments = Enrollment.objects.filter(student=request.user, is_active=True).order_by('-enrolled_at')
    
    # Calculate progress for each enrollment
    for enrollment in enrollments:
        lessons = enrollment.course.lessons.all()
        completed_lessons = 0
        total_lessons = lessons.count()
        
        for lesson in lessons:
            progress, created = CourseProgress.objects.get_or_create(
                student=request.user,
                lesson=lesson,
                defaults={'completed': False}
            )
            if progress.completed:
                completed_lessons += 1
        
        enrollment.completed_lessons = completed_lessons
        enrollment.total_lessons = total_lessons
        enrollment.progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    # Calculate overall statistics
    completed_courses = sum(1 for e in enrollments if e.completed_lessons == e.total_lessons and e.total_lessons > 0)
    total_lessons = sum(e.total_lessons for e in enrollments)
    completed_lessons = sum(e.completed_lessons for e in enrollments)
    
    context = {
        'enrollments': enrollments,
        'completed_courses': completed_courses,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
    }
    return render(request, 'courses/my_courses.html', context)

@login_required
def add_review(request, slug):
    """Add a review for a course"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Check if user is enrolled or has access
    if not course.user_has_access(request.user):
        messages.error(request, 'You need to enroll in this course to leave a review.')
        return redirect('courses:course_detail', slug=slug)
    
    # Check if user has already reviewed
    existing_review = Review.objects.filter(student=request.user, course=course).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, user=request.user, course=course, instance=existing_review)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user
            review.course = course
            
            # Check if this is a verified purchase
            from payment_system.models import Payment
            review.is_verified_purchase = Payment.objects.filter(
                student=request.user,
                course=course,
                status='approved'
            ).exists()
            
            review.save()
            
            if existing_review:
                messages.success(request, 'Your review has been updated successfully!')
            else:
                messages.success(request, 'Thank you for your review!')
            
            return redirect('courses:course_detail', slug=slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm(user=request.user, course=course, instance=existing_review)
    
    context = {
        'form': form,
        'course': course,
        'existing_review': existing_review,
    }
    return render(request, 'courses/add_review.html', context)

def category_courses(request, category_id):
    """Courses by category"""
    category = get_object_or_404(Category, id=category_id)
    courses = Course.objects.filter(category=category, is_published=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'courses/category_courses.html', context)

@login_required
@require_POST
def mark_review_helpful(request, review_id):
    """Mark a review as helpful"""
    review = get_object_or_404(Review, id=review_id, is_moderated=True)
    
    # Check if user has already marked this review as helpful
    if request.user in review.helpful_votes.all():
        review.helpful_votes.remove(request.user)
        review.helpful_count = review.helpful_votes.count()
        review.save()
        return JsonResponse({'success': True, 'helpful': False, 'count': review.helpful_count})
    else:
        review.helpful_votes.add(request.user)
        review.helpful_count = review.helpful_votes.count()
        review.save()
        return JsonResponse({'success': True, 'helpful': True, 'count': review.helpful_count})

@login_required
def edit_review(request, review_id):
    """Edit user's own review"""
    review = get_object_or_404(Review, id=review_id, student=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, user=request.user, course=review.course, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review has been updated successfully!')
            return redirect('courses:course_detail', slug=review.course.slug)
    else:
        form = ReviewForm(user=request.user, course=review.course, instance=review)
    
    context = {
        'form': form,
        'review': review,
        'course': review.course,
    }
    return render(request, 'courses/edit_review.html', context)

@login_required
def delete_review(request, review_id):
    """Delete user's own review"""
    review = get_object_or_404(Review, id=review_id, student=request.user)
    course_slug = review.course.slug
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review has been deleted successfully!')
        return redirect('courses:course_detail', slug=course_slug)
    
    context = {
        'review': review,
        'course': review.course,
    }
    return render(request, 'courses/delete_review.html', context)

@staff_member_required
def moderate_reviews(request):
    """Admin view to moderate reviews"""
    reviews = Review.objects.filter(is_moderated=False).order_by('-created_at')
    
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        action = request.POST.get('action')
        
        if review_id and action:
            review = get_object_or_404(Review, id=review_id)
            
            if action == 'approve':
                review.is_moderated = True
                review.moderated_by = request.user
                review.moderated_at = timezone.now()
                review.save()
                messages.success(request, f'Review by {review.student.username} has been approved.')
            elif action == 'reject':
                review.delete()
                messages.success(request, f'Review by {review.student.username} has been rejected.')
    
    # Pagination
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_pending': reviews.count(),
    }
    return render(request, 'courses/moderate_reviews.html', context)

def review_analytics(request, slug):
    """Review analytics for a course"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Get rating statistics
    rating_form = CourseRatingForm(course)
    rating_stats = rating_form.get_rating_stats()
    
    # Get recent reviews
    recent_reviews = course.get_recent_reviews(10)
    
    # Get rating distribution
    rating_distribution = course.get_rating_distribution()
    
    # Calculate rating distribution with percentages for template
    rating_distribution_with_percentages = {}
    for rating in range(1, 6):
        count = rating_distribution.get(rating, 0)
        percentage = course.get_rating_percentage(rating)
        rating_distribution_with_percentages[rating] = {
            'count': count,
            'percentage': percentage
        }
    
    # Check user access for template
    user_has_access = False
    if request.user.is_authenticated:
        user_has_access = course.user_has_access(request.user)
    
    context = {
        'course': course,
        'rating_stats': rating_stats,
        'recent_reviews': recent_reviews,
        'rating_distribution': rating_distribution,
        'rating_distribution_with_percentages': rating_distribution_with_percentages,
        'user_has_access': user_has_access,
    }
    return render(request, 'courses/review_analytics.html', context)
