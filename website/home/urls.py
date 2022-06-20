from django.urls import path, include
from home import views as home_views

urlpatterns = [
    path('', home_views.home, name='home'),
    path('student/', home_views.student, name='student'),
    path('staff/', home_views.staff, name='staff'),
    path('parent/', home_views.parents, name='parent'),
    path('admin/', include('admin.urls'), name='admin'),
]
