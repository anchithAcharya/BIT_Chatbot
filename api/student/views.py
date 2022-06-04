from urllib import request
from rest_framework import viewsets
from student.models import Student
from student.serializers import (
	StudentCreationSerializer,
	StudentUpdationSerializer_Student,
	StudentUpdationSerializer_Admin
)

from rest_framework.decorators import action
from core.serializers import LoginSerializer
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.utils import timezone
from core.authentication import ExpiringTokenAuthentication
from rest_framework import status
from rest_framework.response import Response

from rest_framework.permissions import AllowAny, IsAuthenticated
from core.permissions import isAdmin, isOwner

from django.conf import settings
from core.models import PasswordResetRequest
from django.core.mail import send_mail
from django.urls import reverse

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class StudentViewSet(viewsets.ModelViewSet):
	queryset = Student.objects.all()
	serializer_class = StudentCreationSerializer
	lookup_field = 'user_id'

	@action(detail=False, methods=['POST'])
	def login(self, request):
		serializer = LoginSerializer(data=request.data)
		if serializer.is_valid():
			try:
				if serializer.validated_data.get('id'): user = get_user_model().objects.get(id=serializer.validated_data['id'])
				else: user = get_user_model().objects.get(email=serializer.validated_data['email'])

			except get_user_model().DoesNotExist:
				return Response(status=status.HTTP_404_NOT_FOUND)

			if not user.check_password(serializer.validated_data['password']):
				return Response(status=status.HTTP_401_UNAUTHORIZED)

			token, created =  Token.objects.get_or_create(user=user)

			utc_now = timezone.now()    
			if not created and token.created < utc_now - ExpiringTokenAuthentication.validity_time:
				token.delete()
				token = Token.objects.create(user=user)
				token.created = timezone.now()
				token.save()

			response_data = {'token': token.key}
			return Response(response_data, content_type="application/json")

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=False, methods=['POST'])
	def logout(self, request):
		request.user.auth_token.delete()
		return Response(status=status.HTTP_200_OK)

	@action(detail=False, methods=['POST'])
	def change_password(self, request):
		# validate data
		data = request.data.copy()
		data['password'] = 'DummyPassword123'
		serializer = LoginSerializer(data=data)

		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


		# get user
		try:
			if serializer.validated_data.get('id'): user = get_user_model().objects.get(id=serializer.validated_data['id'])
			else: user = get_user_model().objects.get(email=serializer.validated_data['email'])

		except get_user_model().DoesNotExist:
			return Response(status=status.HTTP_404_NOT_FOUND)


		# generate password reset request
		req, created = PasswordResetRequest.objects.get_or_create(user=user)

		first_time = not user.has_usable_password()
		time_limit = timezone.timedelta(hours=48) if first_time else timezone.timedelta(minutes=30)

		if not created and req.created < timezone.now() - time_limit:
			req.delete()
			req = PasswordResetRequest.objects.create(user=user)
			req.save()


		# send email
		if user.is_superuser: type = "Admin"
		elif user.is_staff: type = "Student"
		else: type = "Staff"
	
		change_password_url = request.get_host() + reverse(f"{self.basename}-{self.change_password.url_name}")
		reset_password_url = request.get_host() + reverse(f"{self.basename}-{self.password_reset.url_name}")

		send_mail(
			f"BIT Online Portal password account verification" if first_time else f"BIT Online Portal password reset",
			f'''An account has been created for you in the {type} Portal of the BIT website.\n\n
			Please click on the following link to verify the account by setting your password: {reset_password_url}?token={req.key}\n\n
			This link is only valid for the next 48 hours. In order to issue a password-reset request again, visit {change_password_url}
			If you are not {user.name}, then please ignore this email.'''.replace('\t\t', '') if first_time else
			f'''We have received a request to reset the password for your account in the {type} Portal of the BIT website.
			Please click on the following link to reset your password: {reset_password_url}?token={req.key}\n\n
			This link is only valid for the next 30 minutes. In order to issue a password-reset request again, visit {change_password_url}
			If you did not request a password reset, please ignore this email.'''.replace('\t\t', ''),
			"superuser.bit@gmail.com",
			[user.email]
		)
		
		return Response(f"{'Verification' if first_time else 'Password reset'} email sent to {user.email}.", status=status.HTTP_200_OK)

	@action(detail=False, methods=['POST'])
	def password_reset(self, request):
		token = request.GET.get('token')

		try:
			req = PasswordResetRequest.objects.get(key=token)
					
		except PasswordResetRequest.DoesNotExist:
			return Response("Invalid password reset request token.", status=status.HTTP_404_NOT_FOUND)

		user = req.user
		password = request.data.get('password')

		try:
			validate_password(password, user=user)

		except ValidationError as e:
			return Response({'password': e}, status=status.HTTP_400_BAD_REQUEST)

		first_time = not user.has_usable_password()

		if settings.TESTING: time_limit = timezone.timedelta(seconds=15) if first_time else timezone.timedelta(seconds=25)
		else: time_limit = timezone.timedelta(hours=48) if first_time else timezone.timedelta(minutes=30)

		if req.created < timezone.now() - time_limit:
			req.delete()
			return Response("Password reset token expired.", status=status.HTTP_400_BAD_REQUEST)
		
		else:
			user = req.user

			user.set_password(password)
			user.save()
			req.delete()

			return Response(f"Password for user {user} changed successfully.", status=status.HTTP_200_OK)


	def get_serializer_class(self):
		if self.action == 'update' or self.action == 'partial_update':
			if self.request.user.id == self.kwargs['user_id']:
				return StudentUpdationSerializer_Student

			else: return StudentUpdationSerializer_Admin

		return super().get_serializer_class()

	def get_permissions(self):
		if self.action == 'login':
			permissions = {'login': AllowAny}

		elif self.detail:
			permissions = {
			'retrieve': isAdmin|isOwner,
			'update': isAdmin|isOwner,
			'partial_update': isAdmin|isOwner,
			'destroy': isAdmin
		}

		else: permissions = {
			'list': isAdmin,
			'create': isAdmin,
			'login': AllowAny,
			'logout': IsAuthenticated,
			'change_password': AllowAny,
			'password_reset': AllowAny
		}

		self.permission_classes = (permissions[self.action],)
		return super().get_permissions()