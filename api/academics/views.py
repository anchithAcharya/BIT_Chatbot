from rest_framework.decorators import api_view
from rest_framework import viewsets, status
from academics.models import Marks, Attendance, Branch
from academics.serializers import (
	MarksSerializer,
	MarksQuerySerializer,
	AttendanceSerializer,
	AttendanceQuerySerializer
)
from django.db.models import Q
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core.permissions import isAdmin, isStaff, isOwner


@api_view(['GET'])
def get_branch_names(request):
	branches = Branch.objects.all()
	branches = [(branch.code, branch.name) for branch in branches]
	return Response(branches, status.HTTP_200_OK)


class MarksViewSet(viewsets.ModelViewSet):
	queryset = Marks.objects.all()
	serializer_class = MarksSerializer
	lookup_fields = ('student_id', 'subject_id')


	def list(self, request, *args, **kwargs):
		serializer = MarksQuerySerializer(data=request.GET, partial=True)

		if serializer.is_valid():
			student = serializer.validated_data.get('student', {}).get('user', {}).get('id')
			subject_id = serializer.validated_data.get('subject', {}).get('code')
			subject_name = serializer.validated_data.get('subject', {}).get('name')
			semester = serializer.validated_data.get('subject', {}).get('semester')

			queryset = self.filter_queryset(self.get_queryset())
			if student: queryset = queryset.filter(student=student)
			if subject_id: queryset = queryset.filter(subject__code=subject_id)
			if subject_name: queryset = queryset.filter(Q(subject__name=subject_name) | Q(subject__abbreviation=subject_name))
			if semester: queryset = queryset.filter(subject__semester=semester)

			page = self.paginate_queryset(queryset)
			if page is not None:
				serializer = self.get_serializer(page, many=True)
				return self.get_paginated_response(serializer.data)

			serializer = self.get_serializer(queryset, many=True)
			return Response(serializer.data)

		else: return super().list(request, *args, **kwargs)


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


	def list(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.GET, partial=True)

		if serializer.is_valid():
			student = serializer.validated_data.get('student', {}).get('user', {}).get('id')
			subject = serializer.validated_data.get('subject', {}).get('code')

			queryset = self.filter_queryset(self.get_queryset())
			if student: queryset = queryset.filter(student=student)
			if subject: queryset = queryset.filter(subject=subject)

			page = self.paginate_queryset(queryset)
			if page is not None:
				serializer = self.get_serializer(page, many=True)
				return self.get_paginated_response(serializer.data)

			serializer = self.get_serializer(queryset, many=True)
			return Response(serializer.data)

		else: return super().list(request, *args, **kwargs)


	def get_object(self):
		queryset = self.filter_queryset(self.get_queryset())

		filter_kwargs = {field: self.kwargs[field] for field in self.lookup_fields}
		obj = get_object_or_404(queryset, **filter_kwargs)

		self.check_object_permissions(self.request, obj)

		return obj

	def get_permissions(self):
		self.permission_classes = (isStaff|isAdmin|isOwner,)
		return super().get_permissions()