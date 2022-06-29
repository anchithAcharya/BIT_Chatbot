from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from PIL import Image


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
	user = models.OneToOneField(get_user_model(), primary_key=True, on_delete=models.CASCADE, related_name='student')
	image = models.ImageField(default='default.jpg', upload_to='students/', null=True, blank=True)
	current_sem = models.IntegerField(blank=True, default=1)
	branch = models.ForeignKey('academics.Branch', on_delete=models.CASCADE)
	phone = models.CharField(max_length=10, blank=True, default='', validators=[phone_validator])

	def __str__(self):
		return 'Student ' + self.user.id

	def clean(self, *args, **kwargs):
		user_validator(self.user)

		if self.current_sem < 1:
			raise ValidationError('Current semester must be greater than or equal to 1.')

		if self.current_sem > self.branch.max_sems:
			raise ValidationError(f"Current semester must be less than or equal to number or semesters for {self.branch.name}: {self.branch.max_sems}.")

		super(Student, self).clean(*args, **kwargs)

	def save(self, *args, **kwargs):
		self.user.save()
		self.full_clean()
		ret = super(Student, self).save(*args, **kwargs)

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