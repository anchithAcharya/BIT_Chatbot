from django import forms
from common.forms import StudentQueryForm


class CreateStudentForm(forms.Form):
	def __init__(self, *args, **kwargs):
		choices = kwargs.pop('branch_choices', ())
		super().__init__(*args, **kwargs)
		self.fields['branch'].choices = choices

	id = forms.CharField(max_length=15, label='USN')
	email = forms.EmailField(max_length = 254, label='Email')
	name = forms.CharField(max_length=100, label='Name')
	branch = forms.ChoiceField(choices=(), label='Branch')
	current_sem = forms.IntegerField(initial=1, min_value=1, label='Student Semester')

class CreateStaffForm(forms.Form):
	def __init__(self, *args, **kwargs):
		choices = kwargs.pop('branch_choices', ())
		super().__init__(*args, **kwargs)
		self.fields['branch'].choices = choices

	id = forms.CharField(max_length=15, label='USN')
	email = forms.EmailField(max_length = 254, label='Email')
	name = forms.CharField(max_length=100, label='Name')
	branch = forms.ChoiceField(choices=(), label='Branch')


class EditStudentForm(forms.Form):
	name = forms.CharField(max_length=254, label='Name')
	branch = forms.CharField(max_length=64, label='Branch')
	current_sem = forms.IntegerField(label='Current Semester')

class EditStaffForm(forms.Form):
	name = forms.CharField(max_length=254, label='Name')
	branch = forms.CharField(max_length=64, label='Branch')


class StaffQueryForm(StudentQueryForm):
	current_sem = None