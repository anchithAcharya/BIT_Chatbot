from django.urls import path
from . import views as student_views

urlpatterns = [
    path('', student_views.student, name='student'),
    path('home', student_views.home, name='student_home'),
    path('login', student_views.login, name='student_login'),
    path('logout', student_views.logout, name='student_logout'),
    path('logout/success', student_views.logout_success, name='student_logout_success'),
    path('forgot-password', student_views.forgot_password, name='student_forgot_password'),
    path('reset-password', student_views.reset_password, name='student_reset_password'),
    path('change-password', student_views.change_password, name='student_change_password'),

	path('account', student_views.account, name='student_account'),
	path('marks', student_views.marks, name='student_marks'),
	path('attendance', student_views.attendance, name='student_attendance')
]
