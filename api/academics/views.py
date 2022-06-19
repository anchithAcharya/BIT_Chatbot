from rest_framework import viewsets
from academics.models import Marks, Attendance
from academics.serializers import MarksSerializer, AttendanceSerializer
from django.shortcuts import get_object_or_404
from core.permissions import isAdmin, isStaff, isOwner


class MarksViewSet(viewsets.ModelViewSet):
	queryset = Marks.objects.all()
	serializer_class = MarksSerializer
	lookup_fields = ('student_id', 'subject_id')


	def get_object(self):
		queryset = self.filter_queryset(self.get_queryset())

		filter_kwargs = {field: self.kwargs[field] for field in self.lookup_fields}
		obj = get_object_or_404(queryset, **filter_kwargs)

		self.check_object_permissions(self.request, obj)

		return obj

	def get_permissions(self):
		self.permission_classes = (isStaff|isAdmin|isOwner,)
		return super().get_permissions()

class AttendanceViewSet(viewsets.ModelViewSet):
	queryset = Attendance.objects.all()
	serializer_class = AttendanceSerializer
	lookup_fields = ('student_id', 'subject_id')


	def get_object(self):
		queryset = self.filter_queryset(self.get_queryset())

		filter_kwargs = {field: self.kwargs[field] for field in self.lookup_fields}
		obj = get_object_or_404(queryset, **filter_kwargs)

		self.check_object_permissions(self.request, obj)

		return obj

	def get_permissions(self):
		self.permission_classes = (isStaff|isAdmin|isOwner,)
		return super().get_permissions()