from rest_framework import viewsets
from staff.models import Staff
from staff.serializers import (
	StaffDefaultSerializer,
	StaffUpdationSerializer_Staff,
	StaffUpdationSerializer_Admin
)

from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from django.utils import timezone
from core.authentication import ExpiringTokenAuthentication
from rest_framework import status
from rest_framework.response import Response

from rest_framework.permissions import AllowAny, IsAuthenticated
from core.permissions import isAdmin, isCreator

from django.conf import settings
from core.models import PasswordResetRequest
from django.core.mail import send_mail
from django.urls import reverse

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class StaffViewSet(viewsets.ModelViewSet):
	queryset = Staff.objects.all()
	serializer_class = StaffDefaultSerializer
	lookup_field = 'user_id'


	action_permissions = {
		'login': AllowAny,
		'logout': IsAuthenticated,
		'change_password': AllowAny,
		'password_reset': AllowAny
	}

	detail_permissions = {
		'GET': isAdmin|isCreator,
		'PUT': isAdmin|isCreator,
		'PATCH': isAdmin|isCreator,
		'DELETE': isAdmin
	}

	non_detail_permissions = {
		'GET': isAdmin,
		'POST': isAdmin
	}


	@action(detail=False, methods=['POST'])
	def login(self, request):
		# get id/email and password
		id = request.data.get('id')
		password = request.data.get('password')

		errors = {}
		if not id: errors['id'] = "User id or email is required."
		if not password: errors['password'] = "Password is required."

		if errors: return Response(errors, status=status.HTTP_400_BAD_REQUEST)

		# get user
		try:
			user = get_user_model().objects.get(Q(id=id) | Q(email=id))

		except get_user_model().DoesNotExist:
			return Response({'id': "User with the given id/email does not exist."}, status=status.HTTP_404_NOT_FOUND)

		# authenticate user
		user = authenticate(username=user.id, password=password)

		if not user:
			return Response({'password': "Wrong credentials provided."}, status=status.HTTP_401_UNAUTHORIZED)

		# log user in
		login(request, user)

		# create token
		token, created = Token.objects.get_or_create(user=user)

		utc_now = timezone.now()    
		if not created and token.created < utc_now - ExpiringTokenAuthentication.validity_time:
			token.delete()
			token = Token.objects.create(user=user)
			token.created = timezone.now()
			token.save()

		# set token as cookie and return response
		response = Response({'token': token.key}, content_type="application/json")
		response.set_cookie('token', token.key, expires=utc_now+ExpiringTokenAuthentication.validity_time)

		return response

	@action(detail=False, methods=['POST'])
	def logout(self, request):
		request.user.auth_token.delete()
		return Response({'success': "Logged out successfully"}, status=status.HTTP_200_OK)

	@action(detail=False, methods=['POST'])
	def change_password(self, request):
		# get id or email
		id = request.data.get('id')

		if not id:
			return Response({'id': "User id or email is required"}, status=status.HTTP_400_BAD_REQUEST)

		# get user
		try:
			user = get_user_model().objects.get(Q(id=id) | Q(email=id))

		except get_user_model().DoesNotExist:
			return Response({'id': "User with the given id/email does not exist."}, status=status.HTTP_404_NOT_FOUND)


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
		elif user.is_staff: type = "Staff"
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

		return Response(StaffDefaultSerializer(updated_instance).data)

	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		self.perform_destroy(instance.user)
		self.perform_destroy(instance)
		return Response(status=status.HTTP_200_OK)

	def get_serializer_class(self):
		if self.action == 'update' or self.action == 'partial_update':
			if self.request.user.id == self.kwargs['user_id']:
				return StaffUpdationSerializer_Staff

			else: return StaffUpdationSerializer_Admin

		return super().get_serializer_class()

	def get_permissions(self):
		if self.action in self.action_permissions:
			self.permission_classes = (self.action_permissions[self.action],)

		elif self.detail: self.permission_classes = (self.detail_permissions[self.request.method],)
		else: self.permission_classes = (self.non_detail_permissions[self.request.method],)

		return super().get_permissions()