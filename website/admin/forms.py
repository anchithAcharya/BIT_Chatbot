from django import forms


class LoginForm(forms.Form):
	id = forms.CharField(
		max_length=254,
		label='ID/Email',
		widget=forms.TextInput(attrs={'placeholder': 'Enter your ID or email address'}))
	password = forms.CharField(
		widget=forms.PasswordInput(render_value = True, attrs={'placeholder': 'Enter your password'}),
		label='Password')


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
	# email = forms.EmailField(max_length=254, label='Email')
	# phone = forms.CharField(
		# max_length=15, label='Phone',
		# widget=forms.TextInput(attrs={'placeholder': 'Phone number'}))
	branch = forms.CharField(max_length=64, label='Branch')
	current_sem = forms.IntegerField(label='Current Semester')


class EditStaffForm(forms.Form):
	name = forms.CharField(max_length=254, label='Name')
	branch = forms.CharField(max_length=64, label='Branch')