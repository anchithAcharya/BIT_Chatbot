# for User and UserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from validate_email import validate_email


# for PasswordResetRequest
from django.conf import settings
from os import urandom
import binascii


# field validators
def email_validator(value):
	if not settings.TESTING:
		if not validate_email(value):
			raise ValidationError('Invalid email address.')

def name_validator(value):
	import re
	if re.fullmatch("([A-Za-z']{2,30}) ([A-Z]\.? ? )*([A-Za-z']{2,30})? ?([A-Z]\.? ?)*", value) is None:
		raise ValidationError(f'Name {value} is not valid.')


# Custom User model manager
class UserManager(BaseUserManager):
	def create_user(self, id, email, name, user_type, password=None, **extra_fields):
		user = self.model(id=id, email=email, name=name, user_type=user_type, password=password, **extra_fields)

		if password: user.set_password(password)
		else: user.set_unusable_password()

		user.save()
		return user

	def create_superuser(self, id, email, name, password, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')

		if password is None:
			raise ValueError("Superuser must have a password.")

		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')

		return self.create_user(id, email, name, 'Admin', password, **extra_fields)

# Custom User model
class User(AbstractBaseUser, PermissionsMixin):
	id = models.CharField(max_length=10, primary_key=True, unique=True, editable=False)
	email = models.EmailField(max_length=254, unique=True, validators=[email_validator])
	name = models.CharField(max_length=100, null=False, validators=[name_validator])

	is_staff = models.BooleanField(default=False)
	user_type = models.CharField(max_length=10, null=False, editable=False, choices=(
		('Admin', 'Admin'),
		('Student', 'Student'),
		('Staff', 'Staff'),
		('Parent', 'Parent'),
	))

	objects = UserManager()

	USERNAME_FIELD = 'id'
	EMAIL_FIELD = 'email'
	REQUIRED_FIELDS = ['email', 'name']

	def __str__(self):
		return 'User ' + self.id

	def save(self, *args, **kwargs):
		self.full_clean()
		return super(User, self).save(*args, **kwargs)


# Custom model to handle requests for password resets
class PasswordResetRequest(models.Model):
	key = models.CharField("Key", max_length=40, primary_key=True)
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL, related_name='password_reset_request',
		on_delete=models.CASCADE, verbose_name="User"
	)
	created = models.DateTimeField("Created", auto_now_add=True)

	class Meta:
		verbose_name = "PasswordResetRequest"

	def save(self, *args, **kwargs):
		if not self.key:
			self.key = self.generate_key()
		return super().save(*args, **kwargs)

	@classmethod
	def generate_key(cls):
		return binascii.hexlify(urandom(20)).decode()

	def __str__(self):
		return self.key

class ChatbotProblemQuery(models.Model):
	user_email = models.EmailField(max_length=254, unique=False, validators=[email_validator])
	query = models.TextField(verbose_name="Query")
	history = models.TextField(default='[]')
	created = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=10, choices=(
		('Pending', 'Pending'),
		('Ignored', 'Ignored'),
		('Answered', 'Answered'),
	))

	class Meta:
		verbose_name_plural = "ChatbotProblemQueries"

	def __str__(self):
		return f"{self.user_email}: {self.query[:10] + '..' * (len(self.query) > 10)}"