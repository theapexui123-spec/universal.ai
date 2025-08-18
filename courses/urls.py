from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:slug>/enroll/', views.course_enroll, name='course_enroll'),
    path('course/<slug:slug>/learn/', views.course_learn, name='course_learn'),
    path('course/<slug:slug>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('course/<slug:slug>/review/', views.add_review, name='add_review'),
    path('category/<int:category_id>/', views.category_courses, name='category_courses'),
]
