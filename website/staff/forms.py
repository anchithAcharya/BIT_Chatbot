from django import forms
from django.core.exceptions import ValidationError


class EditStaffForm(forms.Form):
	image = forms.ImageField(required=False)
	name = forms.CharField(max_length=254, label='Name', required=False)
	email = forms.EmailField(max_length=254, label='Email', required=False)
	phone = forms.CharField(
		max_length=15, label='Phone', required=False,
		widget=forms.TextInput(attrs={'placeholder': 'Phone number'})
	)

class QueryForm(forms.Form):
	def __init__(self, *args, **kwargs):
		choices = kwargs.pop('branch_choices', ())
		super().__init__(*args, **kwargs)
		self.fields['branch'].choices = choices

	branch = forms.ChoiceField(choices=(), label='Branch', required=False)
	semester = forms.IntegerField(min_value=1, label='Semester', required=False)
	subject = forms.CharField(max_length=100, label='Subject', required=False)
	student = forms.CharField(max_length=100, label='Student', required=False)

class MarksForm(forms.Form):
	def __init__(self, *args, **kwargs):
		edit = kwargs.pop('edit', False)
		super().__init__(*args, **kwargs)

		if edit:
			self.fields['student'].widget.attrs['readonly'] = True
			self.fields['subject'].widget.attrs['readonly'] = True

	student = forms.CharField(max_length=15, label='Student USN', required=True)
	subject = forms.CharField(max_length=15, label='Subject code', required=True)

	test1Marks = forms.IntegerField(min_value=0, label='Test 1 Marks', required=False)
	test2Marks = forms.IntegerField(min_value=0, label='Test 2 Marks', required=False)
	test3Marks = forms.IntegerField(min_value=0, label='Test 3 Marks', required=False)
	assignment1Marks = forms.IntegerField(min_value=0, label='Assignment 1 Marks', required=False)
	assignment2Marks = forms.IntegerField(min_value=0, label='Assignment 2 Marks', required=False)
	externalMarks = forms.IntegerField(min_value=0, label='External exam Marks', required=False)

	test1Total = forms.IntegerField(min_value=0, initial=30, label='Test 1 Total marks', required=False)
	test2Total = forms.IntegerField(min_value=0, initial=30, label='Test 2 Total marks', required=False)
	test3Total = forms.IntegerField(min_value=0, initial=30, label='Test 3 Total marks', required=False)
	assignment1Total = forms.IntegerField(min_value=0, initial=10, label='Assignment 1 Total marks', required=False)
	assignment2Total = forms.IntegerField(min_value=0, initial=10, label='Assignment 2 Total marks', required=False)
	externalTotal = forms.IntegerField(min_value=0, initial=100, label='External exam total marks', required=False)

	def clean(self):
		cd = self.cleaned_data

		map = {
			('test1Marks', cd.get('test1Marks')): ('test1Total', cd.get('test1Total')),
			('test2Marks', cd.get('test2Marks')): ('test2Total', cd.get('test2Total')),
			('test3Marks', cd.get('test3Marks')): ('test3Total', cd.get('test3Total')),
			('assignment1Marks', cd.get('assignment1Marks')): ('assignment1Total', cd.get('assignment1Total')),
			('assignment2Marks', cd.get('assignment2Marks')): ('assignment2Total', cd.get('assignment2Total')),
			('externalMarks', cd.get('externalMarks')): ('externalTota', cd.get('externalTotal'))
		}

		errors = {}

		for marks, total in map.items():
			if marks[1] is not None:
				if marks[1] < 0:
					errors[marks[0]] = 'Marks cannot be negative.'

				if marks[1] > total[1]:
					errors[marks[0]] = f'Marks cannot be greater than total marks: {total[1]}.'

		if errors:
			raise ValidationError(errors)
	
		return super().clean()

class AttendanceForm(forms.Form):
	def __init__(self, *args, **kwargs):
		edit = kwargs.pop('edit', False)
		super().__init__(*args, **kwargs)

		if edit:
			self.fields['student'].widget.attrs['readonly'] = True
			self.fields['subject'].widget.attrs['readonly'] = True

	student = forms.CharField(max_length=15, label='Student USN', required=True)
	subject = forms.CharField(max_length=15, label='Subject code', required=True)

	test1Attendance = forms.DecimalField(min_value=0, max_value=100, decimal_places=2, label='Test 1 Attendance', required=False)
	test2Attendance = forms.DecimalField(min_value=0, max_value=100, decimal_places=2, label='Test 2 Attendance', required=False)
	test3Attendance = forms.DecimalField(min_value=0, max_value=100, decimal_places=2, label='Test 3 Attendance', required=False)