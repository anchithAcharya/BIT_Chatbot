import client.admin as admin_api
import client.common as common_api

from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect

from common.forms import LoginForm, StudentQueryForm
from .forms import (
	EditStudentForm,
	EditStaffForm,
	CreateStudentForm,
	CreateStaffForm,
	StaffQueryForm
)
from django.views.decorators.cache import cache_control
import json


def admin(request):
	if request.COOKIES.get('token'):
		return redirect('admin_home')

	else:
		return redirect('admin_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('admin_login')

	return render(request, 'admin/home.html')

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)

		if form.is_valid():
			response, status_code, cookies = admin_api.login(request.POST.get('id'), request.POST.get('password'))

			if status_code == 200:
				ret = redirect('admin_home')

				for cookie in cookies:
					if cookie.name in ('token', 'csrf_token'):
						ret.set_cookie(cookie.name, cookie.value, expires=cookie.expires)

				return ret

			elif status_code == 401:
				messages.error(request, response.get('password', 'Authentication failed.'))
				ret = redirect('admin_login')
				ret.set_cookie('form_id', form.cleaned_data.get('id'))
				ret.set_cookie('form_password', form.cleaned_data.get('password'))
				return ret

			elif status_code == 404:
				messages.error(request, response.get('id', 'User with given id/email not found.'))
				ret = redirect('admin_login')
				ret.set_cookie('form_id', form.cleaned_data.get('id'))
				ret.set_cookie('form_password', form.cleaned_data.get('password'))
				return ret

			elif status_code == 400:
				for field in response:
					messages.error(request, field+': '+response[field])

				return redirect('admin_login')

		else:
			for field in form.errors:
				messages.error(request, field+': '+form.errors[field])

			return redirect('admin_login')

	else:
		params = {'form': LoginForm({
			'id': request.COOKIES.get('form_id'),
			'password': request.COOKIES.get('form_password')
		})}

		request.COOKIES.pop('form_id', None)
		request.COOKIES.pop('form_password', None)

		return render(request, 'admin/login.html', params)

def logout(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('admin_login')

	response, status_code = admin_api.logout(request.COOKIES.get('token'))

	if status_code == 200:
		messages.success(request, response.get('success', 'Logout successful.'))
		ret = redirect('admin_logout_success')
		ret.delete_cookie('token')
		return ret

	elif status_code == 401:
		messages.error(request, response.get('detail', 'Authentication failed.'))
		return redirect('home')

def logout_success(request):
	return render(request, 'admin/logout_success.html')

def forgot_password(request):
	if request.method == 'POST':
		form = LoginForm({'id': request.POST.get('id'), 'password': 'TestPassword123!'})

		if form.is_valid():
			response, status_code = admin_api.forgot_password(request.POST.get('id'))

			if status_code == 200:
				messages.success(request, response.get('success', 'Password reset mail sent to email associated with this account.'))
				ret = redirect('admin_login')

				ret.delete_cookie('fp_form_id')
				return ret

			elif status_code == 404:
				messages.error(request, response.get('id', 'User with given id/email not found.'))
				ret = redirect('admin_forgot_password')
				ret.set_cookie('fp_form_id', form.cleaned_data.get('id'))
				return ret

			elif status_code == 400:
				for field in response:
					messages.error(request, field+': '+response[field])

				return redirect('admin_forgot_password')

		else:
			for field in form.errors:
				messages.error(request, field+': '+form.errors[field])

			return redirect('admin_forgot_password')

	else:
		params = {'form': LoginForm({
			'id': request.COOKIES.get('fp_form_id'),
		})}

		request.COOKIES.pop('fp_form_id', None)

		return render(request, 'admin/forgot_password.html', params)

def reset_password(request):
	if request.method == 'POST':
		password_reset_token = request.GET.get('token')
		new_password = request.POST.get('password')

		if not password_reset_token:
			messages.error(request, 'Password reset token required.')
			return redirect('admin_forgot_password')

		form = LoginForm({'id': 'TestID123', 'password': new_password})

		if form.is_valid():
			response, status_code = admin_api.reset_password(password_reset_token, new_password)

			if status_code == 200:
				messages.success(request, response.get('success', 'Password reset successful.'))

				ret = redirect('admin_login')
				ret.delete_cookie('rp_form_password')

				return ret

			else:
				if status_code == 404:
					messages.error(request, "Invalid password reset token.")
					return redirect('admin_forgot_password')

				elif status_code == 400:
					if 'password' in response:
						response['password'] = ' '.join(response['password'])
						messages.error(request, "Password: " + response.get('password', "Invalid format for the new password."))

						ret = redirect(reverse('admin_reset_password')+'?token='+password_reset_token)
						ret.set_cookie('rp_form_password', new_password)

						return ret

					elif 'token' in response:
						messages.error(request, response.get('token', "The password reset token you provided has expired."))
						return redirect('admin_forgot_password')

		else:
			for field in form.errors:
				messages.error(request, field + ': ' + form.errors[field])

			return redirect(reverse('admin_reset_password')+'?token='+password_reset_token)
	
	else:
		password_reset_token = request.GET.get('token')
		
		if not password_reset_token:
			messages.error(request, 'Password reset token required.')
			return redirect('admin_forgot_password')

		params = {
			'token': password_reset_token,
			'form': LoginForm({
			'password': request.COOKIES.get('rp_form_password')
		})}

		request.COOKIES.pop('rp_form_password', None)

		return render(request, 'admin/reset_password.html', params)


# Students
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def students(request):
	return redirect('admin_students_dashboard')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_dashboard(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to view the dashboard.')
		return redirect('admin_login')

	token = request.COOKIES.get('token')
	page_no = request.GET.get('page', 1)

	choices, status_code = common_api.get_branch_names(token)
	if status_code == 200: choices.insert(0, ['', 'All'])
	else: choices = ['', 'All']

	form = StudentQueryForm(request.POST, branch_choices=choices)

	if form.is_valid():
		data = {k:v for k,v in form.cleaned_data.items() if v}
		response, status_code = admin_api.get_all_students(token, data, page=page_no)

		if status_code == 200:
			response['total_pages'] = range(1, response['total_pages'] + 1)
			response['form'] = form

			return render(request, 'admin/students/dashboard.html', response)

		else:
			if status_code == 404:
				messages.error(request, f"Invalid or empty page: {page_no}")
				return redirect('admin_students_dashboard')

			elif status_code == 401:
				if request.META.get('HTTP_REFERER') is None:
					messages.error(request, 'Authentication error: ' + response.get('detail', 'Authentication failed.'))

				return redirect('admin_login')

	params = {
		'form': form
	}	

	return render(request, 'admin/students/dashboard.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_details(request, id):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to view student details.')
		return redirect('admin_login')

	initial = json.loads(request.COOKIES.get('initial')) if request.COOKIES.get('initial') else {}
	errors = json.loads(request.COOKIES.get('errors')) if request.COOKIES.get('errors') else {}

	response, status_code = admin_api.get_student_details(request.COOKIES.get('token'), id)

	if status_code == 200:
		for field in initial:
			response[field] = initial[field]

		form = EditStudentForm(response)

		for field in errors:
			form.add_error(field, errors[field])

		ret = render(request, 'admin/students/details.html', {'student': response, 'form': form})
		ret.delete_cookie('initial')
		ret.delete_cookie('errors')

		return ret

	else:
		if status_code == 404:
			messages.error(request, f"User with id '{id}' not found.")
			return redirect(request.META.get('HTTP_REFERER') or 'admin_students_dashboard')

		elif status_code == 401:
			if request.META.get('HTTP_REFERER') is None:
				messages.error(request, 'Authentication error: ' + response.get('detail', 'Authentication failed.'))

			return redirect('admin_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_student(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to view student details.')
		return redirect('admin_login')

	token = request.COOKIES.get('token')

	if request.method == 'POST':
		branches, status_code = common_api.get_branch_names(token)
		if status_code != 200: branches = []

		form = CreateStudentForm(request.POST, request.FILES, branch_choices=branches)

		if form.is_valid():
			response, status_code = admin_api.create_new_student(token, form.cleaned_data)

			if status_code == 201:
				messages.success(request, f"User {response['id']} created successfully.")

				response2, status_code2 = admin_api.forgot_password(response['id'])

				if status_code2 == 200:
					messages.success(request, "Verification email sent to user.")

				else:
					if status_code2 == 404:
						messages.error(request, f"There was a problem sending the verification email: User {response['id']} not found. Please check that the user exists and resend the verification email through the forgot password page.")

					if status_code2 == 400:
						messages.error(request, f"There was a problem sending the verification email. Please resend the verification email through the forgot password page.")

						for field in response2:
							messages.error(request, field+': '+response[field])

				ret = redirect('admin_students_details', id=response['id'])

				for field in form.fields:
					ret.delete_cookie('cstud_form_'+field)

				return ret

			else:
				if status_code == 400:
					for field in response:
						messages.error(request, response[field][0])

					ret = redirect('admin_create_student')
					for field in form.fields:
						ret.set_cookie('cstud_form_'+field, form.cleaned_data[field])

					return ret

				elif status_code == 401:
					if request.META.get('HTTP_REFERER') is None:
						messages.error(request, 'Authentication error: ' + response.get('detail', 'Authentication failed.'))

					return redirect('admin_login')

		else:
			for field in form.errors:
				messages.error(request, f"{field}: {form.errors[field]}")

			ret = redirect('admin_create_student')
			for field in form.fields:
				ret.set_cookie('cstud_form_'+field, form.cleaned_data[field])

			return ret

	else:
		branches, status_code = common_api.get_branch_names(token)
		if status_code != 200: branches = []

		initial={}
		for field in CreateStudentForm.base_fields:
			value = request.COOKIES.get('cstud_form_'+field)
			if value: initial[field] = value
			elif CreateStudentForm.base_fields[field].initial: initial[field] = CreateStudentForm.base_fields[field].initial

		params = {'form': CreateStudentForm(branch_choices=branches)}

		return render(request, 'admin/students/create_student.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_student(request, id):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to edit student details.')
		return redirect('admin_login')

	response, status_code = admin_api.edit_student_details(request.COOKIES.get('token'), id, request.POST)

	if status_code == 200:
		messages.success(request, 'Student details updated successfully.')
		return redirect('admin_students_details', id)

	else:
		if status_code == 404:
			messages.error(request, f"User with id '{id}' not found.")
			return redirect(request.META.get('HTTP_REFERER') or 'admin_students_dashboard')

		elif status_code == 401:
			if request.META.get('HTTP_REFERER') is None:
				messages.error(request, 'Authentication error: ' + response.get('detail', 'Authentication failed.'))

			return redirect('admin_login')

		elif status_code == 400:
			ret = redirect('admin_students_details', id)
			ret.set_cookie('initial', json.dumps(request.POST))
			ret.set_cookie('errors', json.dumps(response))

			return ret

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_student(request, id):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to delete this user.')
		return redirect('admin_login')

	response, status_code = admin_api.delete_student(request.COOKIES.get('token'), id)

	if status_code == 200:
		messages.success(request, response.get('success', 'Student deleted successfully.'))
		return redirect('admin_students_dashboard')


# Staff
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def staff(request):
	return redirect('admin_staff_dashboard')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def staff_dashboard(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to view the dashboard.')
		return redirect('admin_login')

	token = request.COOKIES.get('token')
	page_no = request.GET.get('page', 1)

	choices, status_code = common_api.get_branch_names(token)
	if status_code == 200: choices.insert(0, ['', 'All'])
	else: choices = ['', 'All']

	form = StaffQueryForm(request.POST, branch_choices=choices)

	if form.is_valid():
		data = {k:v for k,v in form.cleaned_data.items() if v}
		response, status_code = admin_api.get_all_staff(token, data, page=page_no)

		if status_code == 200:
			response['total_pages'] = range(1, response['total_pages'] + 1)
			response['form'] = form

			return render(request, 'admin/staff/dashboard.html', response)

		else:
			if status_code == 404:
				messages.error(request, f"Invalid or empty page: {page_no}")
				return redirect('admin_staff_dashboard')

			elif status_code == 401:
				if request.META.get('HTTP_REFERER') is None:
					messages.error(request, 'Authentication error: ' + response.get('detail', 'Authentication failed.'))

				return redirect('admin_login')

	params = {
		'form': form
	}	

	return render(request, 'admin/staff/dashboard.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def staff_details(request, id):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to view staff details.')
		return redirect('admin_login')

	initial = json.loads(request.COOKIES.get('initial')) if request.COOKIES.get('initial') else {}
	errors = json.loads(request.COOKIES.get('errors')) if request.COOKIES.get('errors') else {}

	response, status_code = admin_api.get_staff_details(request.COOKIES.get('token'), id)

	if status_code == 200:
		for field in initial:
			response[field] = initial[field]

		form = EditStaffForm(response)

		for field in errors:
			form.add_error(field, errors[field])

		ret = render(request, 'admin/staff/details.html', {'staff': response, 'form': form})
		ret.delete_cookie('initial')
		ret.delete_cookie('errors')

		return ret

	else:
		if status_code == 404:
			messages.error(request, f"User with id '{id}' not found.")
			return redirect(request.META.get('HTTP_REFERER') or 'admin_staff_dashboard')

		elif status_code == 401:
			if request.META.get('HTTP_REFERER') is None:
				messages.error(request, 'Authentication error: ' + response.get('detail', 'Authentication failed.'))

			return redirect('admin_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_staff(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to view student details.')
		return redirect('admin_login')

	token = request.COOKIES.get('token')

	if request.method == 'POST':
		branches, status_code = common_api.get_branch_names(token)
		if status_code != 200: branches = []

		form = CreateStaffForm(request.POST, request.FILES, branch_choices=branches)

		if form.is_valid():
			response, status_code = admin_api.create_new_staff(token, form.cleaned_data)

			if status_code == 201:
				messages.success(request, "User created successfully.")
				
				response2, status_code2 = admin_api.forgot_password(response['id'])

				if status_code2 == 200:
					messages.success(request, "Verification email sent to user.")

				else:
					if status_code2 == 404:
						messages.error(request, f"There was a problem sending the verification email: User {response['id']} not found. Please check that the user exists and resend the verification email through the forgot password page.")

					if status_code2 == 400:
						messages.error(request, f"There was a problem sending the verification email. Please resend the verification email through the forgot password page.")

						for field in response2:
							messages.error(request, field+': '+response[field])

				ret = redirect('admin_staff_details', id=response['id'])

				for field in form.fields:
					ret.delete_cookie('cstaff_form_'+field)

				return ret

			else:
				if status_code == 400:
					for field in response:
						messages.error(request, response[field][0])

					ret = redirect('admin_create_staff')
					for field in form.fields:
						ret.set_cookie('cstaff_form_'+field, form.cleaned_data[field])

					return ret

				elif status_code == 401:
					if request.META.get('HTTP_REFERER') is None:
						messages.error(request, 'Authentication error: ' + response.get('detail', 'Authentication failed.'))

					return redirect('admin_login')

		else:
			for field in form.errors:
				messages.error(request, f"{field}: {form.errors[field]}")

			ret = redirect('admin_create_staff')
			for field in form.fields:
				ret.set_cookie('cstaff_form_'+field, form.cleaned_data[field])

			return ret

	else:
		branches, status_code = common_api.get_branch_names(token)
		if status_code != 200: branches = []

		initial={}
		for field in CreateStaffForm.base_fields:
			value = request.COOKIES.get('cstaff_form_'+field)
			if value: initial[field] = value
			elif CreateStudentForm.base_fields[field].initial: initial[field] = CreateStaffForm.base_fields[field].initial

		params = {'form': CreateStaffForm(branch_choices=branches)}

		return render(request, 'admin/staff/create_staff.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_staff(request, id):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to edit staff details.')
		return redirect('admin_login')

	response, status_code = admin_api.edit_staff_details(request.COOKIES.get('token'), id, request.POST)

	if status_code == 200:
		messages.success(request, 'Staff details updated successfully.')
		return redirect('admin_staff_details', id)

	else:
		if status_code == 404:
			messages.error(request, f"User with id '{id}' not found.")
			return redirect(request.META.get('HTTP_REFERER') or 'admin_staff_dashboard')

		elif status_code == 401:
			if request.META.get('HTTP_REFERER') is None:
				messages.error(request, 'Authentication error: ' + response.get('detail', 'Authentication failed.'))

			return redirect('admin_login')

		elif status_code == 400:
			ret = redirect('admin_staff_details', id)
			ret.set_cookie('initial', json.dumps(request.POST))
			ret.set_cookie('errors', json.dumps(response))

			return ret

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_staff(request, id):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to delete this user.')
		return redirect('admin_login')

	status_code = admin_api.delete_staff(request.COOKIES.get('token'), id)

	if status_code == 200:
		messages.success(request, 'Staff deleted successfully.')
		return redirect('admin_staff_dashboard')