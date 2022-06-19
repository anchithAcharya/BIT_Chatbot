from rest_framework.routers import DefaultRouter
from staff.views import StaffViewSet


router = DefaultRouter()
router.register('staff', StaffViewSet)