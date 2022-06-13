from django.urls import path
from . import views as admin_views

urlpatterns = [
    path('', admin_views.admin, name='admin'),
    path('login', admin_views.login, name='login'),
    path('logout', admin_views.logout, name='logout'),
    path('dashboard', admin_views.dashboard, name='dashboard'),
]
