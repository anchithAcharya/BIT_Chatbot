from academics.views import MarksViewSet, AttendanceViewSet

from django.urls import path

urlpatterns = [
	path('marks/', MarksViewSet.as_view({
		'get': 'list',
		'post': 'create'
		})
	),
	path('marks/<student_id>-<subject_id>/', MarksViewSet.as_view({
		'get': 'retrieve',
		'put': 'update',
		'patch': 'partial_update',
		'delete': 'destroy'
		})
	),
	path('attendance/<student_id>-<subject_id>/', AttendanceViewSet.as_view({
		'get': 'retrieve',
		'put': 'update',
		'patch': 'partial_update',
		'delete': 'destroy'
		})
	),
]