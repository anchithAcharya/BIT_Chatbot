from rest_framework import viewsets
from student.models import Student
from student.serializers import (
	StudentDefaultSerializer,
	StudentUpdationSerializer_Student,
	StudentUpdationSerializer_Admin,
	StudentQuerySerializer
)

from core.views import (
	core_login,
	core_logout,
	core_forgot_password,
	core_password_reset
)

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from academics.models import Subject, Marks, Attendance
from academics.serializers import MarksSerializer, AttendanceSerializer

from rest_framework.permissions import AllowAny, IsAuthenticated
from core.permissions import isAdmin, isStudent, isStaff


class StudentViewSet(viewsets.ModelViewSet):
	queryset = Student.objects.all()
	serializer_class = StudentDefaultSerializer
	lookup_field = 'user_id'


	action_permissions = {
		'login': AllowAny,
		'logout': IsAuthenticated,
		'forgot_password': AllowAny,
		'password_reset': AllowAny,
		'marks_brief': isStudent,
		'attendance_brief': isStudent,
		'marks_report': isAdmin|isStudent|isStaff,
		'attendance_report': isAdmin|isStudent|isStaff
	}

	detail_permissions = {
		'GET': isAdmin|isStaff|isStudent,
		'PUT': isAdmin|isStudent,
		'PATCH': isAdmin|isStudent,
		'DELETE': isAdmin
	}

	non_detail_permissions = {
		'GET': isAdmin|isStaff,
		'POST': isAdmin
	}


	@action(detail=False, methods=['POST'])
	def login(self, request):
		return core_login(request, user_type='Student')

	@action(detail=False, methods=['POST'])
	def logout(self, request):
		return core_logout(request)

	@action(detail=False, methods=['POST'])
	def forgot_password(self, request):
		return core_forgot_password(request, user_type='Student')

	@action(detail=False, methods=['POST'])
	def password_reset(self, request):
		return core_password_reset(request)


	@action(detail=True, methods=['GET'], url_path='marks/brief')
	def marks_brief(self, request, user_id):
		try:
			student = Student.objects.get(user_id=user_id)

		except Student.DoesNotExist:
			return Response({"token": f"No student with ID {user_id} found."}, status=status.HTTP_404_NOT_FOUND)

		marks = student.marks.filter(subject__semester=student.current_sem)
		marks = MarksSerializer(marks, many=True).data
		return Response(marks, status=status.HTTP_200_OK)

	@action(detail=True, methods=['GET'], url_path='marks/report')
	def marks_report(self, request, user_id):
		try:
			student = Student.objects.get(user_id=user_id)

		except Student.DoesNotExist:
			return Response({"token": f"No student with ID {user_id} found."}, status=status.HTTP_404_NOT_FOUND)

		marks = {}
		for sem in range(1, student.current_sem+1):
			subjects = Subject.objects.filter(branch=student.branch, semester=sem)
			marks[sem] = [student.marks.filter(subject=subject) or [Marks(student=student, subject=subject)] for subject in subjects]
			marks[sem] = [MarksSerializer(mark[0]).data for mark in marks[sem]]

		response = {sem: marks[sem] for sem in marks if marks[sem]}
		response['student_id'] = student.user_id

		return Response(response, status=status.HTTP_200_OK)


	@action(detail=True, methods=['GET'], url_path='attendance/brief')
	def attendance_brief(self, request, user_id):
		try:
			student = Student.objects.get(user_id=user_id)

		except Student.DoesNotExist:
			return Response({"token": f"No student with ID {user_id} found."}, status=status.HTTP_404_NOT_FOUND)

		attendance = student.attendance.filter(subject__semester=student.current_sem)
		attendance = AttendanceSerializer(attendance, many=True).data
		return Response(attendance, status=status.HTTP_200_OK)

	@action(detail=True, methods=['GET'], url_path='attendance/report')
	def attendance_report(self, request, user_id):
		try:
			student = Student.objects.get(user_id=user_id)

		except Student.DoesNotExist:
			return Response({"token": f"No student with ID {user_id} found."}, status=status.HTTP_404_NOT_FOUND)

		attendance = {}
		for sem in range(1, student.current_sem+1):
			subjects = Subject.objects.filter(branch=student.branch, semester=sem)
			attendance[sem] = [student.attendance.filter(subject=subject) or [Attendance(student=student, subject=subject)] for subject in subjects]
			attendance[sem] = [AttendanceSerializer(att[0]).data for att in attendance[sem]]

		response = {sem: attendance[sem] for sem in attendance if attendance[sem]}
		response['student_id'] = student.user_id

		return Response(response, status=status.HTTP_200_OK)


	def list(self, request, *args, **kwargs):
		data=request.GET.copy()
		usn = data.pop('usn', None)
		if usn: data['id'] = usn[0]

		serializer = StudentQuerySerializer(data=data, partial=True)

		if serializer.is_valid():
			id = serializer.validated_data.get('user', {}).get('id')
			email = serializer.validated_data.get('email')
			name = serializer.validated_data.get('user', {}).get('name')
			current_sem = serializer.validated_data.get('current_sem')
			branch = serializer.validated_data.get('branch')
			phone = serializer.validated_data.get('phone')

			queryset = self.filter_queryset(self.get_queryset())
			if id: queryset = queryset.filter(user__id__iexact=id)
			if email: queryset = queryset.filter(user__email__icontains=email)
			if name: queryset = queryset.filter(user__name__icontains=name)
			if current_sem: queryset = queryset.filter(current_sem=current_sem)
			if branch: queryset = queryset.filter(branch__code__icontains=branch)
			if phone: queryset = queryset.filter(phone__contains=phone)

			page = self.paginate_queryset(queryset)
			if page is not None:
				serializer = self.get_serializer(page, many=True)
				return self.get_paginated_response(serializer.data)

			serializer = self.get_serializer(queryset, many=True)
			return Response(serializer.data)

		else: return super().list(request, *args, **kwargs)

	def create(self, request, *args, **kwargs):
		try:
			return super().create(request, *args, **kwargs)

		except ValidationError as e:
			return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

	def update(self, request, *args, **kwargs):
		partial = kwargs.pop('partial', False)
		instance = self.get_object()
		serializer = self.get_serializer(instance, data=request.data, partial=partial)

		errors = {}
		for field in getattr(serializer.Meta, 'restricted', []):
			if field in request.data:
				errors[field] = "You are not authorized to change this field."

		if errors: return Response(errors, status=status.HTTP_400_BAD_REQUEST)

		serializer.is_valid(raise_exception=True)

		try:
			updated_instance = serializer.save()
		except ValidationError as e:
			return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

		if getattr(instance, '_prefetched_objects_cache', None):
			instance._prefetched_objects_cache = {}

		return Response(StudentDefaultSerializer(updated_instance).data)

	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		user_id = instance.user.id

		self.perform_destroy(instance.user)
		self.perform_destroy(instance)

		return Response({'success': f"User {user_id} deleted successfully."}, status=status.HTTP_200_OK)


	def dispatch(self, request, *args, **kwargs):
		try:
			if not self.detail:
				kwargs.pop('user_id', None)

			else:
				req = self.initialize_request(request, *args, **kwargs)
				if kwargs['user_id'] == 'me': kwargs['user_id'] = req.user.id

		except Exception as exc:
			self.headers = self.default_response_headers
			response = self.handle_exception(exc)
			self.response = self.finalize_response(request, response, *args, **kwargs)
			return self.response

		return super().dispatch(request, *args, **kwargs)

	def get_serializer_class(self):
		if self.action == 'update' or self.action == 'partial_update':
			if self.request.user.id == self.kwargs['user_id']:
				return StudentUpdationSerializer_Student

			else: return StudentUpdationSerializer_Admin

		return super().get_serializer_class()

	def get_permissions(self):
		if self.action in self.action_permissions:
			self.permission_classes = (self.action_permissions[self.action],)

		elif self.detail: self.permission_classes = (self.detail_permissions[self.request.method],)
		else: self.permission_classes = (self.non_detail_permissions[self.request.method],)

		return super().get_permissions()