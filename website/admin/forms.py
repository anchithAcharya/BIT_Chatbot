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

	id = forms.CharField(max_length=15, label='ID')
	email = forms.EmailField(max_length = 254, label='Email')
	name = forms.CharField(max_length=100, label='Name')
	branch = forms.ChoiceField(choices=(), label='Branch')

class CreateParentForm(forms.Form):
	id = forms.CharField(max_length=15, label='ID')
	email = forms.EmailField(max_length = 254, label='Email')
	name = forms.CharField(max_length=100, label='Name')
	student = forms.CharField(max_length=20, label='Child USN')
	phone = forms.CharField(max_length=10, label='Phone')


class EditStudentForm(forms.Form):
	name = forms.CharField(max_length=254, label='Name')
	branch = forms.CharField(max_length=64, label='Branch')
	current_sem = forms.IntegerField(label='Current Semester')

class EditStaffForm(forms.Form):
	name = forms.CharField(max_length=254, label='Name')
	branch = forms.CharField(max_length=64, label='Branch')

class EditParentForm(forms.Form):
	name = forms.CharField(max_length=254, label='Name')
	student = forms.CharField(max_length=20, label='Child USN')


class StaffQueryForm(StudentQueryForm):
	usn = None
	current_sem = None

	id = forms.CharField(label='Staff ID', required=False)

class ParentQueryForm(StaffQueryForm):
	id = forms.CharField(label='Parent ID', required=False)
	name = forms.CharField(label='Name', required=False)
	email = forms.CharField(label='Email', required=False)
	phone = forms.CharField(label='Phone', required=False)