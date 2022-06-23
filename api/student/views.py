from rest_framework import viewsets
from student.models import Student
from student.serializers import (
	StudentDefaultSerializer,
	StudentUpdationSerializer_Student,
	StudentUpdationSerializer_Admin
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
from academics.serializers import MarksSerializer, AttendanceSerializer

from rest_framework.permissions import AllowAny, IsAuthenticated
from core.permissions import isAdmin, isCreator, isStudent, isStaff


class StudentViewSet(viewsets.ModelViewSet):
	queryset = Student.objects.all()
	serializer_class = StudentDefaultSerializer
	lookup_field = 'user_id'


	action_permissions = {
		'login': AllowAny,
		'logout': IsAuthenticated,
		'forgot_password': AllowAny,
		'password_reset': AllowAny,
		'account': isStudent,
		'marks': isAdmin|isCreator|isStaff,
		'attendance': isAdmin|isCreator|isStaff
	}

	detail_permissions = {
		'GET': isAdmin|isCreator|isStaff,
		'PUT': isAdmin|isCreator,
		'PATCH': isAdmin|isCreator,
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


	@action(detail=True, methods=['GET'])
	def marks(self, request, user_id=None):
		student = Student.objects.get(user_id=user_id)
		marks = student.marks.filter(subject__semester=student.current_sem)
		marks = MarksSerializer(marks, many=True).data
		return Response(marks, status=status.HTTP_200_OK)

	@action(detail=True, methods=['GET'])
	def attendance(self, request, user_id=None):
		student = Student.objects.get(user_id=user_id)
		attendance = student.attendance.filter(subject__semester=student.current_sem)
		attendance = AttendanceSerializer(attendance, many=True).data
		return Response(attendance, status=status.HTTP_200_OK)


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
		updated_instance = serializer.save()

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
		if not self.detail:
			kwargs.pop('user_id', None)

		else:
			req = self.initialize_request(request, *args, **kwargs)
			kwargs['user_id'] = req.user.id

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