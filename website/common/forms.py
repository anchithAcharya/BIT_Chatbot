from django import forms


class LoginForm(forms.Form):
	id = forms.CharField(
		max_length=254,
		label='ID/Email',
		widget=forms.TextInput(attrs={'placeholder': 'Enter your ID or email address'}))
	password = forms.CharField(
		widget=forms.PasswordInput(render_value = True, attrs={'placeholder': 'Enter your password'}),
		label='Password')

class PasswordResetForm(forms.Form):
	old_password = forms.CharField(
		label='Current Password',
		widget=forms.PasswordInput(render_value = True, attrs={'placeholder': 'Enter your current password'}))
	password = forms.CharField(
		label='New Password',
		widget=forms.PasswordInput(render_value = True, attrs={'placeholder': 'Enter your new password'}))
	password_confirm = forms.CharField(
		label='Confirm Password',
		widget=forms.PasswordInput(render_value = True, attrs={'placeholder': 'Confirm your new password'}))

	def clean(self):
		if 'password' in self.cleaned_data and 'password_confirm' in self.cleaned_data:
			if self.cleaned_data['password'] != self.cleaned_data['password_confirm']:
				raise forms.ValidationError('Passwords do not match.')

class StudentQueryForm(forms.Form):
	def __init__(self, *args, **kwargs):
		choices = kwargs.pop('branch_choices', ())
		super().__init__(*args, **kwargs)
		self.fields['branch'].choices = choices

	usn = forms.CharField(label='USN', required=False)
	name = forms.CharField(label='Name', required=False)
	email = forms.CharField(label='Email', required=False)
	phone = forms.CharField(label='Phone', required=False)
	branch = forms.ChoiceField(label='Branch', required=False)
	current_sem = forms.CharField(label='Current Semester', required=False)
