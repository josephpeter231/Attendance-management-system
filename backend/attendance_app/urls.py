from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('accounts/login/', views.user_login, name='login'),  # Add this line
    path('add_attendance/', views.add_attendance, name='add_attendance'),
    path('attendance/summary/<int:user_id>/', views.user_attendance_summary, name='user_attendance_summary'),
]
