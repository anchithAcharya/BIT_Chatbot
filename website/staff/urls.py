from django.urls import path
from . import views as staff_views

urlpatterns = [
    path('', staff_views.staff, name='staff'),
    path('home', staff_views.home, name='staff_home'),
    path('login', staff_views.login, name='staff_login'),
    path('logout', staff_views.logout, name='staff_logout'),
    path('logout/success', staff_views.logout_success, name='staff_logout_success'),
    path('forgot-password', staff_views.forgot_password, name='staff_forgot_password'),
    path('reset-password', staff_views.reset_password, name='staff_reset_password'),
    path('change-password', staff_views.change_password, name='staff_change_password'),

	path('account', staff_views.account, name='staff_account'),
	path('student-details', staff_views.student_details, name='staff_student_details'),

	path('marks', staff_views.list_marks, name='staff_list_marks'),
	path('marks/add', staff_views.add_marks, name='staff_add_marks'),
	path('marks/detail', staff_views.detail_marks, name='staff_detail_marks'),

	path('attendance', staff_views.list_attendance, name='staff_list_attendance'),
	path('attendance/add', staff_views.add_attendance, name='staff_add_attendance'),
	path('attendance/detail', staff_views.detail_attendance, name='staff_detail_attendance'),
]
