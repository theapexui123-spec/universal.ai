from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/lazy-load/', views.lazy_load_courses, name='lazy_load_courses'),  # New lazy loading endpoint
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:slug>/enroll/', views.course_enroll, name='course_enroll'),
    path('course/<slug:slug>/learn/', views.course_learn, name='course_learn'),
    path('course/<slug:slug>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('course/<slug:slug>/review/', views.add_review, name='add_review'),
    path('category/<int:category_id>/', views.category_courses, name='category_courses'),
    
    # Review-related URLs
    path('review/<int:review_id>/helpful/', views.mark_review_helpful, name='mark_review_helpful'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('course/<slug:slug>/analytics/', views.review_analytics, name='review_analytics'),
    path('admin/moderate-reviews/', views.moderate_reviews, name='moderate_reviews'),
]
