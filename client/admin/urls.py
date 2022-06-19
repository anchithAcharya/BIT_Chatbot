from django.urls import path
from . import views as admin_views

urlpatterns = [
    path('', admin_views.admin, name='admin'),
    path('home', admin_views.home, name='admin_home'),
    path('login', admin_views.login, name='admin_login'),
    path('logout', admin_views.logout, name='admin_logout'),
    path('logout/success', admin_views.logout_success, name='admin_logout_success'),
    path('students', admin_views.students, name='admin_students'),
    path('students/dashboard', admin_views.student_dashboard, name='admin_students_dashboard'),
    path('students/detail/<id>', admin_views.student_details, name='admin_students_details'),
    path('students/edit/<id>', admin_views.edit_student, name='admin_students_edit'),
    path('students/delete/<id>', admin_views.delete_student, name='admin_students_delete'),
    # path('staff', admin_views.dashboard, name='staff'),
    # path('parents', admin_views.dashboard, name='parents'),
]
