from PIL import Image
from django.db import models
from student.models import Student
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


def user_validator(value):
	value.full_clean()

def phone_validator(value):
	errors = []

	if len(value) != 10:
		errors.append(ValidationError('Phone number must be 10 digits.'))

	if value.isdigit() is False:
		errors.append(ValidationError('Phone number must be numeric.'))

	if errors: raise ValidationError(errors)


class Parent(models.Model):
	user = models.OneToOneField(get_user_model(), primary_key=True, on_delete=models.CASCADE, related_name='parent')
	image = models.ImageField(default='default.jpg', upload_to='students/', null=True, blank=True)
	student = models.ForeignKey(Student, to_field='user', on_delete=models.CASCADE, related_name='prnts', null=True)
	phone = models.CharField(max_length=10, blank=True, default='', validators=[phone_validator])

	def __str__(self):
		return 'Parent ' + self.user.id

	def clean(self, *args, **kwargs):
		user_validator(self.user)
		super(Parent, self).clean(*args, **kwargs)

	def save(self, *args, **kwargs):
		self.user.save()
		self.full_clean()
		ret = super(Parent, self).save(*args, **kwargs)

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