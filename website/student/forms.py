from django import forms

class EditStudentForm(forms.Form):
	image = forms.ImageField(required=False)
	name = forms.CharField(max_length=254, label='Name', required=False)
	email = forms.EmailField(max_length=254, label='Email', required=False)
	phone = forms.CharField(
		max_length=15, label='Phone', required=False,
		widget=forms.TextInput(attrs={'placeholder': 'Phone number'})
	)