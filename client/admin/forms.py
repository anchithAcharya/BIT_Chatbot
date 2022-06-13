from django import forms


class LoginForm(forms.Form):
	id = forms.CharField(
		max_length=254,
		label='ID/Email',
		widget=forms.TextInput(attrs={'placeholder': 'Enter your ID or email address'}))
	password = forms.CharField(
		widget=forms.PasswordInput(render_value = True, attrs={'placeholder': 'Enter your password'}),
		label='Password')