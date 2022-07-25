from rest_framework.decorators import api_view
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework import viewsets
from django.core.mail import send_mail
from .models import ChatbotProblemQuery
from rest_framework.response import Response
from core.models import PasswordResetRequest
from django.contrib.auth import get_user_model
from .serializers import ChatbotQuerySerializer
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login as auth_login
from core.authentication import ExpiringTokenAuthentication
from django.contrib.auth.password_validation import validate_password


def core_login(request, user_type='Admin'):
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

	# validate user type
	if user.user_type != user_type:
		if user_type == 'Admin':
			return Response({'id': f"User with id {id} is not an admin."}, status=status.HTTP_400_BAD_REQUEST)

		elif user_type == 'Student':
			return Response({'id': f"User with id {id} is not a student."}, status=status.HTTP_400_BAD_REQUEST)

		elif user_type == 'Staff':
			return Response({'id': f"User with id {id} is not a staff member."}, status=status.HTTP_400_BAD_REQUEST)

		elif user_type == 'Parent':
			return Response({'id': f"User with id {id} is not a parent."}, status=status.HTTP_400_BAD_REQUEST)

	# authenticate user
	user = authenticate(username=user.id, password=password)

	if not user:
		return Response({'password': "Wrong credentials provided."}, status=status.HTTP_401_UNAUTHORIZED)

	# log user in
	auth_login(request, user)

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

def core_logout(request):
	request.user.auth_token.delete()
	return Response({'success': "Logged out successfully"}, status=status.HTTP_200_OK)

def core_forgot_password(request, user_type='Admin'):
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
	forgot_password_url = settings.FORGOT_PASSWORD_URL.replace('type', user.user_type.lower())
	reset_password_url = f"{settings.RESET_PASSWORD_URL.replace('type', user.user_type.lower())}?token={req.key}"

	send_mail(
		f"BIT Online Portal password account verification" if first_time else f"BIT Online Portal password reset",
		f'''An account has been created for you in the {user_type} Portal of the BIT website.\n\n
		Please click on the following link to verify the account by setting your password: {reset_password_url}\n\n
		This link is only valid for the next 48 hours. In order to issue a password-reset request again, visit {forgot_password_url}
		If you are not {user.name}, then please ignore this email.'''.replace('\t\t', '') if first_time else
		f'''We have received a request to reset the password for your account in the {user_type} Portal of the BIT website.
		Please click on the following link to reset your password: {reset_password_url}\n\n
		This link is only valid for the next 30 minutes. In order to issue a password-reset request again, visit {forgot_password_url}
		If you did not request a password reset, please ignore this email.'''.replace('\t\t', ''),
		"superuser.bit@gmail.com",
		[user.email]
	)
	
	return Response({'success': f"{'Verification' if first_time else 'Password reset'} email sent to {user.email}."}, status=status.HTTP_200_OK)

def core_password_reset(request):
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
		return Response({'token': "Password reset token expired."}, status=status.HTTP_400_BAD_REQUEST)
	
	else:
		user = req.user

		user.set_password(password)
		user.save()
		req.delete()

		return Response({'success': f"Password for user {user} changed successfully."}, status=status.HTTP_200_OK)


@api_view(['POST'])
def login(request):
	return core_login(request)

@api_view(['POST'])
def logout(request):
	return core_logout(request)

@api_view(['POST'])
def forgot_password(request):
	return core_forgot_password(request)

@api_view(['POST'])
def password_reset(request):
	return core_password_reset(request)


class ChatbotProblemQueryViewSet(viewsets.ModelViewSet):
	queryset = ChatbotProblemQuery.objects.all()
	serializer_class = ChatbotQuerySerializer