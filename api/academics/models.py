from django.db import models
from student.models import Student
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


def get_abbreviation(name):
	abbreviation = ''

	for word in name.split():
		if word[0].isupper():
			abbreviation += word[0]

	return abbreviation

class Branch(models.Model):
	code = models.CharField(primary_key=True, max_length=10, editable=False)
	name = models.CharField(max_length=100)
	max_sems = models.IntegerField(default=8)

	class Meta:
		verbose_name_plural = "branches"

	def __str__(self):
		return self.name

class Subject(models.Model):
	code = models.CharField(max_length=10, primary_key=True, editable=False)
	name = models.CharField(max_length=100)
	abbreviation = models.CharField(max_length=10, blank=False, default=get_abbreviation)
	branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
	semester = models.IntegerField()
	credits = models.IntegerField()

	def __str__(self):
		return self.name

	def clean(self) -> None:
		if self.semester < 1:
			raise ValidationError('Current semester must be greater than or equal to 1.')

		if self.semester > self.branch.max_sems:
			raise ValidationError(f"Current semester must be less than or equal to number or semesters for {self.branch.name}: {self.branch.max_sems}.")

		return super().clean()

class Marks(models.Model):
	student = models.ForeignKey(Student, null=True, on_delete=models.SET_NULL, related_name = 'marks')
	subject = models.ForeignKey(Subject, null=True, on_delete=models.CASCADE)

	test1Marks = models.IntegerField(null=True, blank=True)
	test2Marks = models.IntegerField(null=True, blank=True)
	test3Marks = models.IntegerField(null=True, blank=True)
	assignment1Marks = models.IntegerField(null=True, blank=True)
	assignment2Marks = models.IntegerField(null=True, blank=True)
	externalMarks = models.IntegerField(null=True, blank=True)

	test1Total = models.IntegerField(default=30, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
	test2Total = models.IntegerField(default=30, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
	test3Total = models.IntegerField(default=30, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
	assignment1Total = models.IntegerField(default=10, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
	assignment2Total = models.IntegerField(default=10, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
	externalTotal = models.IntegerField(default=100, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])

	class Meta:
		verbose_name_plural = "marks"
		constraints = [
			models.UniqueConstraint(
				fields=['student', 'subject'], name='student_subject_combination_marks'
			)
		]

	def __str__(self):
		return f"<{self.student.user.id} {self.subject.name} marks>"

	def clean(self) -> None:
		map = {
			('test1Marks', self.test1Marks): ('test1Total', self.test1Total),
			('test2Marks', self.test2Marks): ('test2Total', self.test2Total),
			('test3Marks', self.test3Marks): ('test3Total', self.test3Total),
			('assignment1Marks', self.assignment1Marks): ('assignment1Total', self.assignment1Total),
			('assignment2Marks', self.assignment2Marks): ('assignment2Total', self.assignment2Total),
			('externalMarks', self.externalMarks): ('externalTota', self.externalTotal)
		}

		errors = {}

		for marks, total in map.items():
			if marks[1] is not None:
				if marks[1] < 0:
					errors[marks[0]] = 'Marks cannot be negative.'

				if marks[1] > total[1]:
					errors[marks[0]] = f'Marks cannot be greater than total marks: {total[1]}.'

		if self.subject.semester > self.student.current_sem:
			errors['subject'] = f"Student current semester is {self.student.current_sem} but subject semester is {self.subject.semester}."

		if errors:
			raise ValidationError(errors)

class Attendance(models.Model):
	student = models.ForeignKey(Student, null=True, on_delete=models.SET_NULL, related_name='attendance')
	subject = models.ForeignKey(Subject, null=True, on_delete=models.CASCADE)

	test1Attendance = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2, validators = [MinValueValidator(0), MaxValueValidator(100)])
	test2Attendance = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2, validators = [MinValueValidator(0), MaxValueValidator(100)])
	test3Attendance = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2, validators = [MinValueValidator(0), MaxValueValidator(100)])

	class Meta:
		verbose_name_plural = "attendance"
		constraints = [
			models.UniqueConstraint(
				fields=['student', 'subject'], name='student_subject_combination_attendance'
			)
		]

	def __str__(self):
		return f"<{self.student.user.id} {self.subject.name} attendance>"