from django.urls import path
from . import views as parent_views

urlpatterns = [
    path('', parent_views.parent, name='parent'),
    path('home', parent_views.home, name='parent_home'),
    path('login', parent_views.login, name='parent_login'),
    path('logout', parent_views.logout, name='parent_logout'),
    path('logout/success', parent_views.logout_success, name='parent_logout_success'),
    path('forgot-password', parent_views.forgot_password, name='parent_forgot_password'),
    path('reset-password', parent_views.reset_password, name='parent_reset_password'),
    path('change-password', parent_views.change_password, name='parent_change_password'),

	path('account', parent_views.account, name='parent_account'),
	path('student', parent_views.student_account, name='parent_student_account'),
	path('marks', parent_views.marks, name='parent_student_marks'),
	path('attendance', parent_views.attendance, name='parent_student_attendance')
]
