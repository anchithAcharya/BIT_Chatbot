from django.urls import path
from core.views import login, logout, forgot_password, password_reset

urlpatterns = [
	path('admin/login/', login, name='admin_login'),
	path('admin/logout/', logout, name='admin_logout'),
	path('admin/forgot_password/', forgot_password, name='admin_forgot_password'),
	path('admin/password_reset/', password_reset, name='admin_password_reset'),
]