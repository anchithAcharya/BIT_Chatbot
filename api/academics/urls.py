from academics.views import MarksViewSet, AttendanceViewSet, get_branch_names

from django.urls import path

urlpatterns = [
	path('metadata/branches/', get_branch_names, name='get_branch_names'),
	path('marks/', MarksViewSet.as_view({
		'get': 'list',
		'post': 'create'
		})
	),
	path('attendance/', AttendanceViewSet.as_view({
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
	)
]