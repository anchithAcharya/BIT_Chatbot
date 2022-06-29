from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from PIL import Image

from django.contrib.auth.models import BaseUserManager

# field validators
def user_validator(value):
	value.full_clean()

def phone_validator(value):
	errors = []

	if len(value) != 10:
		errors.append(ValidationError('Phone number must be 10 digits.'))

	if value.isdigit() is False:
		errors.append(ValidationError('Phone number must be numeric.'))

	if errors: raise ValidationError(errors)


class StaffManager(BaseUserManager):
	def create(self, *args, **extra_fields):
		staff = super().create(*args, **extra_fields)
		staff.user.is_staff = True
		staff.save()
		return staff

# Staff class
class Staff(models.Model):
	user = models.OneToOneField(get_user_model(), primary_key=True, on_delete=models.CASCADE, related_name='staff')
	image = models.ImageField(default='default.jpg', upload_to='staff/', null=True, blank=True)
	branch = models.ForeignKey('academics.Branch', on_delete=models.CASCADE)
	phone = models.CharField(max_length=10, blank=True, default='', validators=[phone_validator])

	objects = StaffManager()

	class Meta:
		verbose_name_plural = "staff"

	def __str__(self):
		return "Staff " + self.user.id

	def clean(self, *args, **kwargs):
		user_validator(self.user)
		super(Staff, self).clean(*args, **kwargs)

	def save(self, *args, **kwargs):
		self.user.save()
		self.full_clean()
		ret = super(Staff, self).save(*args, **kwargs)

		if self.image:
			img = Image.open(self.image.path)
		
			if img.height > 300 or img.width > 300:
				output_size = (300, 300)
				img.thumbnail(output_size)
				img.save(self.image.path)

		return ret

	def get_readonly_fields(self, request, obj=None):
			if obj: # editing an existing object
				return self.readonly_fields + ('user',)

			return self.readonly_fields