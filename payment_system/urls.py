from django.urls import path
from . import views

app_name = 'payment_system'

urlpatterns = [
    path('course/<slug:slug>/pay/', views.payment_page, name='payment_page'),
    path('payment/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('payment/<int:payment_id>/status/', views.payment_status, name='payment_status'),
    path('my-payments/', views.my_payments, name='my_payments'),
    path('instructions/', views.payment_instructions, name='payment_instructions'),
    
    # Admin URLs
    path('admin/payments/', views.admin_payments, name='admin_payments'),
    path('admin/payment/<int:payment_id>/approve/', views.approve_payment, name='approve_payment'),
    path('admin/payment/<int:payment_id>/reject/', views.reject_payment, name='reject_payment'),
    path('admin/methods/', views.payment_methods_admin, name='payment_methods_admin'),
    path('admin/method/<int:method_id>/toggle/', views.toggle_payment_method, name='toggle_payment_method'),
]
