"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from core.urls import urlpatterns as admin_urls
from student.urls import router as student_router
from staff.urls import router as staff_router
from parents.urls import router as parent_router
from academics.urls import urlpatterns as academics_urls
from django.conf import settings
from django.conf.urls.static import  static

urlpatterns = [
    path('api/test/admin/', admin.site.urls),
    path('api/', include(admin_urls)),
    path('api/', include(student_router.urls), kwargs={'user_id': 'me'}),
    path('api/', include(staff_router.urls), kwargs={'user_id': 'me'}),
    path('api/', include(parent_router.urls), kwargs={'user_id': 'me'}),
    path('api/', include(academics_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)