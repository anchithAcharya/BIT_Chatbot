from django import forms


class LoginForm(forms.Form):
	id = forms.CharField(
		max_length=254,
		label='ID/Email',
		widget=forms.TextInput(attrs={'placeholder': 'Enter your ID or email address'}))
	password = forms.CharField(
		widget=forms.PasswordInput(render_value = True, attrs={'placeholder': 'Enter your password'}),
		label='Password')

class EditStudentForm(forms.Form):
	name = forms.CharField(max_length=254, label='Name')
	# email = forms.EmailField(max_length=254, label='Email')
	# phone = forms.CharField(
		# max_length=15, label='Phone',
		# widget=forms.TextInput(attrs={'placeholder': 'Phone number'}))
	branch = forms.CharField(max_length=64, label='Branch')
	current_sem = forms.IntegerField(label='Current Semester')