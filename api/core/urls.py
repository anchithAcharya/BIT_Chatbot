from rest_framework import routers
from django.urls import path, include
from .views import ChatbotProblemQueryViewSet
from core.views import login, logout, forgot_password, password_reset

ChatbotProblemQueryRouter = routers.DefaultRouter()
ChatbotProblemQueryRouter.register('chatbot-query', ChatbotProblemQueryViewSet)

urlpatterns = [
	path('admin/login/', login, name='admin_login'),
	path('admin/logout/', logout, name='admin_logout'),
	path('admin/forgot_password/', forgot_password, name='admin_forgot_password'),
	path('admin/password_reset/', password_reset, name='admin_password_reset'),
	path('api/', include(ChatbotProblemQueryRouter.urls)),
]