from rest_framework import viewsets, status
from academics.models import Marks, Attendance, Branch
from rest_framework.decorators import api_view
from academics.serializers import (
	MarksSerializer,
	MarksQuerySerializer,
	AttendanceSerializer,
	AttendanceQuerySerializer
)
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core.permissions import isAdmin, isStaff, isOwner, isStudentsParent


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
		data = request.GET.copy()
		subject = data.pop('subject', None)
		student = data.pop('student', None)

		if subject:
			subject = subject[0]
			data['subject_id'] = subject
			data['subject_name'] = subject

		if student:
			student = student[0]
			data['student_id'] = student
			data['student_name'] = student

		serializer = MarksQuerySerializer(data=data, partial=True)

		if serializer.is_valid():
			student_id = serializer.validated_data.get('student', {}).get('user', {}).get('id')
			student_name = serializer.validated_data.get('student', {}).get('user', {}).get('name')
			subject_id = serializer.validated_data.get('subject', {}).get('code')
			subject_name = serializer.validated_data.get('subject', {}).get('name')
			semester = serializer.validated_data.get('subject', {}).get('semester')
			branch = serializer.validated_data.get('student', {}).get('branch')

			subject = subject_id or subject_name
			student = student_id or student_name

			queryset = self.filter_queryset(self.get_queryset())
			if student: queryset = queryset.filter(Q(student_id_iexact=student) | Q(student__user__name__icontains=student))
			if subject: queryset = queryset.filter(Q(subject__name__icontains=subject) | Q(subject__abbreviation__icontains=subject) | Q(subject__code_iexact=subject))
			if semester: queryset = queryset.filter(subject__semester=semester)
			if branch: queryset = queryset.filter(subject__branch=branch)

			page = self.paginate_queryset(queryset)
			if page is not None:
				serializer = self.get_serializer(page, many=True)
				return self.get_paginated_response(serializer.data)

			serializer = self.get_serializer(queryset, many=True)
			return Response(serializer.data)

		else: return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


	def create(self, *args, **kwargs):
		try:
			return super().create(*args, **kwargs)

		except ValidationError as e:
			return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

	def update(self, *args, **kwargs):
		try:
			return super().update(*args, **kwargs)

		except ValidationError as e:
			return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)


	def get_object(self):
		queryset = self.filter_queryset(self.get_queryset())

		filter_kwargs = {field: self.kwargs[field] for field in self.lookup_fields}
		obj = get_object_or_404(queryset, **filter_kwargs)

		self.check_object_permissions(self.request, obj)

		return obj

	def get_permissions(self):
		self.permission_classes = (isStaff|isAdmin|isOwner|isStudentsParent,)
		return super().get_permissions()

class AttendanceViewSet(viewsets.ModelViewSet):
	queryset = Attendance.objects.all()
	serializer_class = AttendanceSerializer
	lookup_fields = ('student_id', 'subject_id')


	def list(self, request, *args, **kwargs):
		data = request.GET.copy()
		subject = data.pop('subject', None)
		student = data.pop('student', None)

		if subject:
			subject = subject[0]
			data['subject_id'] = subject
			data['subject_name'] = subject

		if student:
			student = student[0]
			data['student_id'] = student
			data['student_name'] = student

		serializer = AttendanceQuerySerializer(data=data, partial=True)

		if serializer.is_valid():
			student_id = serializer.validated_data.get('student', {}).get('user', {}).get('id')
			student_name = serializer.validated_data.get('student', {}).get('user', {}).get('name')
			subject_id = serializer.validated_data.get('subject', {}).get('code')
			subject_name = serializer.validated_data.get('subject', {}).get('name')
			semester = serializer.validated_data.get('subject', {}).get('semester')
			branch = serializer.validated_data.get('student', {}).get('branch')

			subject = subject_id or subject_name
			student = student_id or student_name

			queryset = self.filter_queryset(self.get_queryset())
			if student: queryset = queryset.filter(Q(student_id__iexact=student) | Q(student__user__name__icontains=student))
			if subject: queryset = queryset.filter(Q(subject__name__icontains=subject) | Q(subject__abbreviation__icontains=subject) | Q(subject__code__iexact=subject))
			if semester: queryset = queryset.filter(subject__semester=semester)
			if branch: queryset = queryset.filter(subject__branch=branch)

			page = self.paginate_queryset(queryset)
			if page is not None:
				serializer = self.get_serializer(page, many=True)
				return self.get_paginated_response(serializer.data)

			serializer = self.get_serializer(queryset, many=True)
			return Response(serializer.data)

		else: return super().list(request, *args, **kwargs)


	def create(self, *args, **kwargs):
		try:
			return super().create(*args, **kwargs)

		except ValidationError as e:
			return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

	def update(self, *args, **kwargs):
		try:
			return super().update(*args, **kwargs)

		except ValidationError as e:
			return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)


	def get_object(self):
		queryset = self.filter_queryset(self.get_queryset())

		filter_kwargs = {field: self.kwargs[field] for field in self.lookup_fields}
		obj = get_object_or_404(queryset, **filter_kwargs)

		self.check_object_permissions(self.request, obj)

		return obj

	def get_permissions(self):
		self.permission_classes = (isStaff|isAdmin|isOwner|isStudentsParent,)
		return super().get_permissions()