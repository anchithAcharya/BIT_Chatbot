from django.urls import path, include
from common import views as home_views

urlpatterns = [
    path('', home_views.home, name='home'),
    path('student/', include('student.urls'), name='student'),
    path('staff/', include('staff.urls'), name='staff'),
    path('parent/', home_views.parents, name='parent'),
    path('admin/', include('admin.urls'), name='admin'),
]
