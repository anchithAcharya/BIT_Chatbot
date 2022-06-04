from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


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


# Student class
class Student(models.Model):
	user = models.OneToOneField(get_user_model(), null=True, on_delete=models.CASCADE, related_name='student')
	current_sem = models.IntegerField(default=1)
	branch = models.CharField(max_length=5)
	phone = models.CharField(max_length=10, blank=True, default='', validators=[phone_validator])

	def clean(self, *args, **kwargs):
		user_validator(self.user)
		super(Student, self).clean(*args, **kwargs)

	def save(self, *args, **kwargs):
		self.user.save()
		self.full_clean()
		return super(Student, self).save(*args, **kwargs)