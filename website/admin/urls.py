from django.urls import path
from . import views as admin_views

urlpatterns = [
    path('', admin_views.admin, name='admin'),
    path('home', admin_views.home, name='admin_home'),
    path('login', admin_views.login, name='admin_login'),
    path('logout', admin_views.logout, name='admin_logout'),
    path('logout/success', admin_views.logout_success, name='admin_logout_success'),
    path('forgot-password', admin_views.forgot_password, name='admin_forgot_password'),
    path('reset-password', admin_views.reset_password, name='admin_reset_password'),

    path('students', admin_views.students, name='admin_students'),
    path('students/dashboard', admin_views.student_dashboard, name='admin_students_dashboard'),
    path('students/detail/<id>', admin_views.student_details, name='admin_students_details'),
    path('students/create', admin_views.create_student, name='admin_create_student'),
    path('students/edit/<id>', admin_views.edit_student, name='admin_students_edit'),
    path('students/delete/<id>', admin_views.delete_student, name='admin_students_delete'),

    path('staff', admin_views.staff, name='admin_staff'),
    path('staff/dashboard', admin_views.staff_dashboard, name='admin_staff_dashboard'),
    path('staff/detail/<id>', admin_views.staff_details, name='admin_staff_details'),
    path('staff/create', admin_views.create_staff, name='admin_create_staff'),
    path('staff/edit/<id>', admin_views.edit_staff, name='admin_staff_edit'),
    path('staff/delete/<id>', admin_views.delete_staff, name='admin_staff_delete'),

    path('parents', admin_views.parents, name='admin_parents'),
    path('parents/dashboard', admin_views.parents_dashboard, name='admin_parents_dashboard'),
    path('parents/detail/<id>', admin_views.parents_details, name='admin_parents_details'),
    path('parents/create', admin_views.create_parents, name='admin_create_parents'),
    path('parents/edit/<id>', admin_views.edit_parents, name='admin_parents_edit'),
    path('parents/delete/<id>', admin_views.delete_parents, name='admin_parents_delete'),
]
