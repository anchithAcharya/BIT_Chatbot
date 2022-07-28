from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control

from client import parents as parent_api

from common.forms import LoginForm, PasswordResetForm
from .forms import EditParentForm


def parent(request):
	if request.COOKIES.get('token'):
		return redirect('parent_home')

	else:
		return redirect('parent_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('parent_login')

	token = request.COOKIES.get('token')

	parent, status_code = parent_api.get_account_details(token)

	if status_code != 200:
		messages.error(request, 'There was a problem fetching your account details. Please login again.')
		return redirect('parent_login')

	params = {
		'parent': parent,
	}

	return render(request, 'parent/home.html', params)

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)

		if form.is_valid():
			response, status_code, cookies = parent_api.login(request.POST.get('id'), request.POST.get('password'))

			if status_code == 200:
				ret = redirect('parent_home')

				for cookie in cookies:
					if cookie.name in ('token', 'csrf_token'):
						ret.set_cookie(cookie.name, cookie.value, expires=cookie.expires)

				return ret

			elif status_code == 401:
				messages.error(request, response.get('password', 'Authentication failed.'))
				ret = redirect('parent_login')
				ret.set_cookie('form_id', form.cleaned_data.get('id'))
				ret.set_cookie('form_password', form.cleaned_data.get('password'))
				return ret

			elif status_code == 404:
				messages.error(request, response.get('id', 'User with given id/email not found.'))
				ret = redirect('parent_login')
				ret.set_cookie('form_id', form.cleaned_data.get('id'))
				ret.set_cookie('form_password', form.cleaned_data.get('password'))
				return ret

			elif status_code == 400:
				for field in response:
					messages.error(request, field+': '+response[field])

				return redirect('parent_login')

		else:
			for field in form.errors:
				messages.error(request, field+': '+form.errors[field])

			return redirect('parent_login')

	else:
		params = {'form': LoginForm({
			'id': request.COOKIES.get('form_id'),
			'password': request.COOKIES.get('form_password')
		})}

		request.COOKIES.pop('form_id', None)
		request.COOKIES.pop('form_password', None)

		return render(request, 'parent/login.html', params)

def logout(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('parent_login')

	response, status_code = parent_api.logout(request.COOKIES.get('token'))

	if status_code == 200:
		messages.success(request, response.get('success', 'Logout successful.'))
		ret = redirect('parent_logout_success')
		ret.delete_cookie('token')
		return ret

	elif status_code == 401:
		messages.error(request, response.get('detail', 'Authentication failed.'))
		return redirect('home')

def logout_success(request):
	return render(request, 'parent/logout_success.html')

def forgot_password(request):
	if request.method == 'POST':
		form = LoginForm({'id': request.POST.get('id'), 'password': 'TestPassword123!'})

		if form.is_valid():
			response, status_code = parent_api.forgot_password(request.POST.get('id'))

			if status_code == 200:
				messages.success(request, response.get('success', 'Password reset mail sent to email associated with this account.'))
				ret = redirect('parent_login')

				ret.delete_cookie('fp_form_id')
				return ret

			elif status_code == 404:
				messages.error(request, response.get('id', 'User with given id/email not found.'))
				ret = redirect('parent_forgot_password')
				ret.set_cookie('fp_form_id', form.cleaned_data.get('id'))
				return ret

			elif status_code == 400:
				for field in response:
					messages.error(request, field+': '+response[field])

				return redirect('parent_forgot_password')

		else:
			for field in form.errors:
				messages.error(request, field+': '+form.errors[field])

			return redirect('parent_forgot_password')

	else:
		params = {'form': LoginForm({
			'id': request.COOKIES.get('fp_form_id'),
		})}

		request.COOKIES.pop('fp_form_id', None)

		return render(request, 'parent/forgot_password.html', params)

def reset_password(request):
	if request.method == 'POST':
		password_reset_token = request.GET.get('token')
		new_password = request.POST.get('password')

		if not password_reset_token:
			messages.error(request, 'Password reset token required.')
			return redirect('parent_forgot_password')

		form = LoginForm({'id': 'TestID123', 'password': new_password})

		if form.is_valid():
			response, status_code = parent_api.reset_password(password_reset_token, new_password)

			if status_code == 200:
				messages.success(request, response.get('success', 'Password reset successful.'))

				ret = redirect('parent_login')
				ret.delete_cookie('rp_form_password')

				return ret

			else:
				if status_code == 404:
					messages.error(request, "Invalid password reset token.")
					return redirect('parent_forgot_password')

				elif status_code == 400:
					if 'password' in response:
						response['password'] = ' '.join(response['password'])
						messages.error(request, "Password: " + response.get('password', "Invalid format for the new password."))

						ret = redirect(reverse('parent_reset_password')+'?token='+password_reset_token)
						ret.set_cookie('rp_form_password', new_password)

						return ret

					elif 'token' in response:
						messages.error(request, response.get('token', "The password reset token you provided has expired."))
						return redirect('parent_forgot_password')

		else:
			for field in form.errors:
				messages.error(request, field+': '+form.errors[field])

			return redirect(reverse('parent_reset_password')+'?token='+password_reset_token)
	
	else:
		password_reset_token = request.GET.get('token')
		
		if not password_reset_token:
			messages.error(request, 'Password reset token required.')
			return redirect('parent_forgot_password')

		params = {
			'token': password_reset_token,
			'form': LoginForm({
			'password': request.COOKIES.get('rp_form_password')
		})}

		request.COOKIES.pop('rp_form_password', None)

		return render(request, 'parent/reset_password.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def change_password(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('staff_login')

	if request.method == 'POST':
		form = PasswordResetForm(request.POST)

		if form.is_valid():
			response, status_code = parent_api.change_password(request.COOKIES.get('token'), form.cleaned_data)

			if status_code == 200:
				messages.success(request, 'Password changed successfully.')
				ret = redirect('parent_login')
				ret.delete_cookie('token')
				return ret

			else:
				if status_code == 401:
					messages.error(request, 'Authentication failed.')
					return redirect('parent_login')

				if status_code == 400:
					for field in response:
						form.add_error(field, response[field])

		return render(request, 'parent/change_password.html', {'form': form})

	else:
		return render(request, 'parent/change_password.html', {'form': PasswordResetForm()})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def account(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('parent_login')

	token = request.COOKIES.get('token')

	parent, status_code1 = parent_api.get_account_details(token)

	if status_code1 != 200:
		messages.error(request, f"There was an error fetching your account details: {parent}")
		return redirect('parent_home')

	if request.method == 'POST':
		form = EditParentForm(request.POST, request.FILES)

		if form.is_valid():
			data = form.cleaned_data.copy()
			image = data.pop('image', None)
			files = {'image': (image.name, image.read(), image.content_type)} if image else {}

			response, status_code = parent_api.edit_account_details(token, parent['id'], data, files)

			if status_code == 200:
				messages.success(request, "Account details updated successfully.")
				return redirect('parent_account')

			else:
				if status_code == 401:
					messages.error(request, response.get('detail', 'Authentication failed.'))
					return redirect('parent_login')

				elif status_code == 400:
					for field in response:
						form.add_error(field, response[field])

		params = {
			'parent': parent,
			'form': form
		}

		return render(request, 'parent/account.html', params)

	else:
		params = {
			'parent': parent,
			'form': EditParentForm(parent)
		}

		return render(request, 'parent/account.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_account(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('parent_login')

	token = request.COOKIES.get('token')

	student, status_code = parent_api.get_student_details(token)

	if status_code != 200:
		messages.error(request, f"There was an error fetching your student details.")
		return redirect('parent_home')

	return render(request, 'parent/student_account.html', {'student': student})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def marks(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('parent_login')

	response, status_code = parent_api.get_student_marks_report(request.COOKIES.get('token'))

	if status_code == 200:
		params = {
			'student_id': response.pop('student_id', None),
			'marks_report': response
			}
		return render(request, 'parent/marks.html', params)

	else:
		if status_code == 401:
			messages.error(request, response.get('detail', 'Authentication failed.'))
			return redirect('parent_login')

		else:
			messages.error(request, "There was an error fetching your marks report.")
			return redirect('parent_home')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def attendance(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('parent_login')

	response, status_code = parent_api.get_student_attendance_report(request.COOKIES.get('token'))

	if status_code == 200:
		params = {
			'student_id': response.pop('student_id', None),
			'attendance_report': response
			}
		return render(request, 'parent/attendance.html', params)

	else:
		if status_code == 401:
			messages.error(request, response.get('detail', 'Authentication failed.'))
			return redirect('parent_login')

		else:
			messages.error(request, "There was an error fetching your attendance report.")
			return redirect('parent_home')
