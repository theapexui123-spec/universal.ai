from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Course, Category, Enrollment, Review, CourseProgress, Lesson
from payment_system.models import Payment, PaymentMethod, PaymentSettings

def home(request):
    """Landing page with featured courses"""
    featured_courses = Course.objects.filter(is_published=True, is_featured=True)[:6]
    latest_courses = Course.objects.filter(is_published=True).order_by('-created_at')[:6]
    categories = Category.objects.all()[:8]
    
    context = {
        'featured_courses': featured_courses,
        'latest_courses': latest_courses,
        'categories': categories,
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
    
    # Check if user is enrolled
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists()
    
    # Get lessons
    lessons = course.lessons.all()
    
    # Get reviews
    reviews = course.reviews.all().order_by('-created_at')[:5]
    
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
        'reviews': reviews,
        'related_courses': related_courses,
        'is_enrolled': is_enrolled,
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
    """Course learning page for enrolled students"""
    course = get_object_or_404(Course, slug=slug)
    
    # Check if user is enrolled
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)
    
    # Get lessons with progress
    lessons = course.lessons.all()
    lesson_progress = {}
    
    for lesson in lessons:
        progress, created = CourseProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson,
            defaults={'completed': False}
        )
        lesson_progress[lesson.id] = progress
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'lessons': lessons,
        'lesson_progress': lesson_progress,
    }
    return render(request, 'courses/course_learn.html', context)

@login_required
def lesson_detail(request, slug, lesson_id):
    """Individual lesson page"""
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    # Check if user is enrolled
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)
    
    # Get or create progress
    progress, created = CourseProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson,
        defaults={'completed': False}
    )
    
    # Get next and previous lessons
    lessons = list(course.lessons.all())
    current_index = lessons.index(lesson)
    next_lesson = lessons[current_index + 1] if current_index < len(lessons) - 1 else None
    prev_lesson = lessons[current_index - 1] if current_index > 0 else None
    
    context = {
        'course': course,
        'lesson': lesson,
        'progress': progress,
        'next_lesson': next_lesson,
        'prev_lesson': prev_lesson,
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
    
    context = {
        'enrollments': enrollments,
    }
    return render(request, 'courses/my_courses.html', context)

@login_required
def add_review(request, slug):
    """Add a review for a course"""
    if request.method == 'POST':
        course = get_object_or_404(Course, slug=slug)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            # Check if user has already reviewed
            review, created = Review.objects.get_or_create(
                student=request.user,
                course=course,
                defaults={'rating': rating, 'comment': comment}
            )
            
            if not created:
                review.rating = rating
                review.comment = comment
                review.save()
            
            # Update course rating
            avg_rating = course.reviews.aggregate(Avg('rating'))['rating__avg']
            course.rating = avg_rating or 0
            course.total_ratings = course.reviews.count()
            course.save()
            
            messages.success(request, 'Review submitted successfully!')
        else:
            messages.error(request, 'Please provide both rating and comment.')
    
    return redirect('course_detail', slug=slug)

def category_courses(request, category_id):
    """Courses by category"""
    category = get_object_or_404(Category, id=category_id)
    courses = Course.objects.filter(category=category, is_published=True).order_by('-created_at')
    
    context = {
        'category': category,
        'courses': courses,
    }
    return render(request, 'courses/category_courses.html', context)
