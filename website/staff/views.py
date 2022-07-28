from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control

from client import staff as staff_api
from client import common as common_api

from common.forms import (
	LoginForm,
	PasswordResetForm,
	StudentQueryForm
)
from .forms import (
	EditStaffForm,
	QueryForm,
	MarksForm,
	AttendanceForm
)


def staff(request):
	if request.COOKIES.get('token'):
		return redirect('staff_home')

	else:
		return redirect('staff_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('staff_login')

	token = request.COOKIES.get('token')

	staff, status_code = staff_api.get_account_details(token)

	if status_code != 200:
		messages.error(request, 'There was a problem fetching your account details. Please login again.')
		return redirect('staff_login')

	params = {
		'staff': staff,
	}

	return render(request, 'staff/home.html', params)

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)

		if form.is_valid():
			response, status_code, cookies = staff_api.login(request.POST.get('id'), request.POST.get('password'))

			if status_code == 200:
				ret = redirect('staff_home')

				for cookie in cookies:
					if cookie.name in ('token', 'csrf_token'):
						ret.set_cookie(cookie.name, cookie.value, expires=cookie.expires)

				return ret

			elif status_code == 401:
				messages.error(request, response.get('password', 'Authentication failed.'))
				ret = redirect('staff_login')
				ret.set_cookie('form_id', form.cleaned_data.get('id'))
				ret.set_cookie('form_password', form.cleaned_data.get('password'))
				return ret

			elif status_code == 404:
				messages.error(request, response.get('id', 'User with given id/email not found.'))
				ret = redirect('staff_login')
				ret.set_cookie('form_id', form.cleaned_data.get('id'))
				ret.set_cookie('form_password', form.cleaned_data.get('password'))
				return ret

			elif status_code == 400:
				for field in response:
					messages.error(request, field+': '+response[field])

				return redirect('staff_login')

		else:
			for field in form.errors:
				messages.error(request, field+': '+form.errors[field])

			return redirect('staff_login')

	else:
		params = {'form': LoginForm({
			'id': request.COOKIES.get('form_id'),
			'password': request.COOKIES.get('form_password')
		})}

		request.COOKIES.pop('form_id', None)
		request.COOKIES.pop('form_password', None)

		return render(request, 'staff/login.html', params)

def logout(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('staff_login')

	response, status_code = staff_api.logout(request.COOKIES.get('token'))

	if status_code == 200:
		messages.success(request, response.get('success', 'Logout successful.'))
		ret = redirect('staff_logout_success')
		ret.delete_cookie('token')
		return ret

	elif status_code == 401:
		messages.error(request, response.get('detail', 'Authentication failed.'))
		return redirect('home')

def logout_success(request):
	return render(request, 'staff/logout_success.html')

def forgot_password(request):
	if request.method == 'POST':
		form = LoginForm({'id': request.POST.get('id'), 'password': 'TestPassword123!'})

		if form.is_valid():
			response, status_code = staff_api.forgot_password(request.POST.get('id'))

			if status_code == 200:
				messages.success(request, response.get('success', 'Password reset mail sent to email associated with this account.'))
				ret = redirect('staff_login')

				ret.delete_cookie('fp_form_id')
				return ret

			elif status_code == 404:
				messages.error(request, response.get('id', 'User with given id/email not found.'))
				ret = redirect('staff_forgot_password')
				ret.set_cookie('fp_form_id', form.cleaned_data.get('id'))
				return ret

			elif status_code == 400:
				for field in response:
					messages.error(request, field+': '+response[field])

				return redirect('staff_forgot_password')

		else:
			for field in form.errors:
				messages.error(request, field+': '+form.errors[field])

			return redirect('staff_forgot_password')

	else:
		params = {'form': LoginForm({
			'id': request.COOKIES.get('fp_form_id'),
		})}

		request.COOKIES.pop('fp_form_id', None)

		return render(request, 'staff/forgot_password.html', params)

def reset_password(request):
	if request.method == 'POST':
		password_reset_token = request.GET.get('token')
		new_password = request.POST.get('password')

		if not password_reset_token:
			messages.error(request, 'Password reset token required.')
			return redirect('staff_forgot_password')

		form = LoginForm({'id': 'TestID123', 'password': new_password})

		if form.is_valid():
			response, status_code = staff_api.reset_password(password_reset_token, new_password)

			if status_code == 200:
				messages.success(request, response.get('success', 'Password reset successful.'))

				ret = redirect('staff_login')
				ret.delete_cookie('rp_form_password')

				return ret

			else:
				if status_code == 404:
					messages.error(request, "Invalid password reset token.")
					return redirect('staff_forgot_password')

				elif status_code == 400:
					if 'password' in response:
						response['password'] = ' '.join(response['password'])
						messages.error(request, "Password: " + response.get('password', "Invalid format for the new password."))

						ret = redirect(reverse('staff_reset_password')+'?token='+password_reset_token)
						ret.set_cookie('rp_form_password', new_password)

						return ret

					elif 'token' in response:
						messages.error(request, response.get('token', "The password reset token you provided has expired."))
						return redirect('staff_forgot_password')

		else:
			for field in form.errors:
				messages.error(request, field+': '+form.errors[field])

			return redirect(reverse('staff_reset_password')+'?token='+password_reset_token)
	
	else:
		password_reset_token = request.GET.get('token')
		
		if not password_reset_token:
			messages.error(request, 'Password reset token required.')
			return redirect('staff_forgot_password')

		params = {
			'token': password_reset_token,
			'form': LoginForm({
			'password': request.COOKIES.get('rp_form_password')
		})}

		request.COOKIES.pop('rp_form_password', None)

		return render(request, 'staff/reset_password.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def change_password(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('staff_login')

	if request.method == 'POST':
		form = PasswordResetForm(request.POST)

		if form.is_valid():
			response, status_code = staff_api.change_password(request.COOKIES.get('token'), form.cleaned_data)

			if status_code == 200:
				messages.success(request, 'Password changed successfully.')
				ret = redirect('staff_login')
				ret.delete_cookie('token')
				return ret

			else:
				if status_code == 401:
					messages.error(request, 'Authentication failed.')
					return redirect('staff_login')

				if status_code == 400:
					for field in response:
						form.add_error(field, response[field])

		return render(request, 'staff/change_password.html', {'form': form})

	else:
		return render(request, 'staff/change_password.html', {'form': PasswordResetForm()})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def account(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('staff_login')

	token = request.COOKIES.get('token')

	staff, status_code1 = staff_api.get_account_details(token)

	if status_code1 != 200:
		messages.error(request, f"There was an error fetching your account details: {staff}")
		return redirect('staff_home')

	if request.method == 'POST':
		form = EditStaffForm(request.POST, request.FILES)

		if form.is_valid():
			data = form.cleaned_data.copy()
			image = data.pop('image', None)
			files = {'image': (image.name, image.read(), image.content_type)} if image else {}

			response, status_code = staff_api.edit_account_details(token, data, files)

			if status_code == 200:
				messages.success(request, "Account details updated successfully.")
				return redirect('staff_account')

			else:
				if status_code == 401:
					messages.error(request, response.get('detail', 'Authentication failed.'))
					return redirect('staff_login')

				elif status_code == 400:
					for field in response:
						form.add_error(field, response[field])

		params = {
			'staff': staff,
			'form': form
		}

		return render(request, 'staff/account.html', params)

	else:
		params = {
			'staff': staff,
			'form': EditStaffForm(staff)
		}

		return render(request, 'staff/account.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_details(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to view the student details.')
		return redirect('staff_login')

	token = request.COOKIES.get('token')
	page_no = request.GET.get('page', 1)

	choices, status_code = common_api.get_branch_names(token)
	if status_code == 200: choices.insert(0, ['', 'All'])
	else: choices = ['', 'All']

	form = StudentQueryForm(request.POST, branch_choices=choices)

	if form.is_valid():
		data = {k:v for k,v in form.cleaned_data.items() if v}
		response, status_code = staff_api.get_all_students(token, data, page=page_no)

		if status_code == 200:
			response['total_pages'] = range(1, response['total_pages'] + 1)
			response['form'] = form

			return render(request, 'staff/student_details.html', response)

		else:
			if status_code == 404:
				messages.error(request, f"Invalid or empty page: {page_no}")
				return redirect('staff_student_details')

			elif status_code == 401:
				if request.META.get('HTTP_REFERER') is None:
					messages.error(request, 'Authentication error: ' + response.get('detail', 'Authentication failed.'))

				return redirect('staff_login')

	params = {
		'form': form
	}	

	return render(request, 'staff/student_details.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def list_marks(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('staff_login')

	token = request.COOKIES.get('token')

	choices, status_code = common_api.get_branch_names(token)
	if status_code == 200: choices.insert(0, ['', 'All'])
	else: choices = ['', 'All']

	form = QueryForm(request.POST, branch_choices=choices)
	page = request.GET.get('page', 1)

	if form.is_valid():
		data = {k:v for k,v in form.cleaned_data.items() if v}
		response, status_code = common_api.get_all_marks(token, **data, page=page)

		if status_code == 200:
			params = {
				'form': form,
				'all_marks': response.get('results', []),
				'total_pages': range(1, response.get('total_pages', 1)+1),
				'next_page_no': response.get('next_page_no', None),
				'prev_page_no': response.get('prev_page_no', None)
			}

			marks = {}
			for mark in params['all_marks']:
				if mark['student'] in marks: marks[mark['student']].append(mark)
				else: marks[mark['student']] = [mark]

			params['all_marks'] = marks

			return render(request, 'staff/marks/all_marks.html', params)

		else:
			if status_code == 401:
				messages.error(request, response.get('detail', 'Authentication failed.'))
				return redirect('staff_login')

			elif status_code == 400:
				for field in response:
					form.add_error(field, response[field])

	params = {
		'form': form,
		'all_marks': []
	}

	for mark in params['all_marks']:
		if mark['student'] in marks: marks[mark['student']].append(mark)
		else: marks[mark['student']] = [mark]

	params['all_marks'] = marks

	return render(request, 'staff/marks/all_marks.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detail_marks(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('staff_login')

	token = request.COOKIES.get('token')

	if not request.GET.get('student'):
		messages.error(request, 'Student ID required in URL parameters.')
		return redirect('staff_list_marks')

	if not request.GET.get('subject'):
		messages.error(request, 'Subject code required in URL parameters.')
		return redirect('staff_list_marks')

	student = request.GET.get('student')
	subject = request.GET.get('subject')

	if request.method == 'POST':
		form = MarksForm(request.POST, edit=True)

		if form.is_valid():
			response, status_code = common_api.edit_marks_details(token, student, subject, form.cleaned_data)

			if status_code == 200:
				messages.success(request, "Marks updated successfully.")
				return redirect('staff_list_marks')

			else:
				if status_code == 401:
					messages.error(request, response.get('detail', 'Authentication failed.'))
					return redirect('staff_login')

				elif status_code == 404:
					messages.error(request, response.get('detail', 'Marks record not found.'))
					return redirect('staff_list_marks')

				elif status_code == 400:
					if type(response) is dict:
						for field in response:
							form.add_error(field, response[field])

					else: messages.error(request, response[0])

		params = {
			'action': reverse('staff_detail_marks')+'?student='+student+'&subject='+subject,
			'form': form,
			'student': student,
			'subject': subject
		}

		return render(request, 'staff/marks/detail_marks.html', params)

	else:
		details, status_code = common_api.get_marks_details(token, student, subject)

		if status_code != 200:
			messages.error(request, f"There was an error fetching the marks details: {details}")
			return redirect('staff_list_marks')

		params = {
			'action': reverse('staff_detail_marks')+'?student='+student+'&subject='+subject,
			'form': MarksForm(details, edit=True),
			'student': student,
			'subject': subject
		}

		return render(request, 'staff/marks/detail_marks.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_marks(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('staff_login')

	token = request.COOKIES.get('token')

	if request.method == 'POST':
		form = MarksForm(request.POST)

		if form.is_valid():
			response, status_code = common_api.add_marks(token, form.cleaned_data)

			if status_code == 201:
				messages.success(request, "Marks added successfully.")
				return redirect('staff_list_marks')

			else:
				if status_code == 401:
					messages.error(request, response.get('detail', 'Authentication failed.'))
					return redirect('staff_login')

				elif status_code == 400:
					for field in response:
						form.add_error(field, response[field])

		params = {
			'action': reverse('staff_add_marks'),
			'add': True,
			'form': form
		}

		return render(request, 'staff/marks/detail_marks.html', params)

	else:
		params = {
			'action': reverse('staff_add_marks'),
			'add': True,
			'form': MarksForm()
		}

		return render(request, 'staff/marks/detail_marks.html', params)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def list_attendance(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('staff_login')

	token = request.COOKIES.get('token')

	choices, status_code = common_api.get_branch_names(token)
	if status_code == 200: choices.insert(0, ['', 'All'])
	else: choices = ['', 'All']

	form = QueryForm(request.POST, branch_choices=choices)
	page = request.GET.get('page', 1)

	if form.is_valid():
		data = {k:v for k,v in form.cleaned_data.items() if v}
		response, status_code = common_api.get_all_attendance(token, **data, page=page)

		if status_code == 200:
			params = {
				'form': form,
				'all_attendance': response.get('results', []),
				'total_pages': range(1, response.get('total_pages', 1)+1),
				'next_page_no': response.get('next_page_no', None),
				'prev_page_no': response.get('prev_page_no', None)
			}

			attendance = {}
			for att in params['all_attendance']:
				if att['student'] in attendance: attendance[att['student']].append(att)
				else: attendance[att['student']] = [att]

			params['all_attendance'] = attendance

			return render(request, 'staff/attendance/all_attendance.html', params)

		else:
			if status_code == 401:
				messages.error(request, response.get('detail', 'Authentication failed.'))
				return redirect('staff_login')

			elif status_code == 400:
				for field in response:
					form.add_error(field, response[field])

	params = {
		'form': form,
		'all_attendance': []
	}

	for att in params['all_attendance']:
		if att['student'] in attendance: attendance[att['student']].append(att)
		else: attendance[att['student']] = [att]

	params['all_attendance'] = attendance

	return render(request, 'staff/attendance/all_attendance.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detail_attendance(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('staff_login')

	token = request.COOKIES.get('token')

	if not request.GET.get('student'):
		messages.error(request, 'Student ID required in URL parameters.')
		return redirect('staff_list_attendance')

	if not request.GET.get('subject'):
		messages.error(request, 'Subject code required in URL parameters.')
		return redirect('staff_list_attendance')

	student = request.GET.get('student')
	subject = request.GET.get('subject')

	if request.method == 'POST':
		form = AttendanceForm(request.POST, edit=True)

		if form.is_valid():
			response, status_code = common_api.edit_attendance_details(token, student, subject, form.cleaned_data)

			if status_code == 200:
				messages.success(request, "Attendance updated successfully.")
				return redirect('staff_list_attendance')

			else:
				if status_code == 401:
					messages.error(request, response.get('detail', 'Authentication failed.'))
					return redirect('staff_login')

				elif status_code == 404:
					messages.error(request, response.get('detail', 'Attendance record not found.'))
					return redirect('staff_list_attendance')

				elif status_code == 400:
					if type(response) is dict:
						for field in response:
							form.add_error(field, response[field])

					else: messages.error(request, response[0])

		params = {
			'action': reverse('staff_detail_attendance')+'?student='+student+'&subject='+subject,
			'form': form,
			'student': student,
			'subject': subject
		}

		return render(request, 'staff/attendance/detail_attendance.html', params)

	else:
		details, status_code = common_api.get_attendance_details(token, student, subject)

		if status_code != 200:
			messages.error(request, f"There was an error fetching the attendance details: {details}")
			return redirect('staff_list_attendance')

		params = {
			'action': reverse('staff_detail_attendance')+'?student='+student+'&subject='+subject,
			'form': AttendanceForm(details, edit=True),
			'student': student,
			'subject': subject
		}

		return render(request, 'staff/attendance/detail_attendance.html', params)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_attendance(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('staff_login')

	token = request.COOKIES.get('token')

	if request.method == 'POST':
		form = AttendanceForm(request.POST)

		if form.is_valid():
			response, status_code = common_api.add_attendance(token, form.cleaned_data)

			if status_code == 201:
				messages.success(request, "Attendance added successfully.")
				return redirect('staff_list_attendance')

			else:
				if status_code == 401:
					messages.error(request, response.get('detail', 'Authentication failed.'))
					return redirect('staff_login')

				elif status_code == 400:
					for field in response:
						form.add_error(field, response[field])

		params = {
			'action': reverse('staff_add_attendance'),
			'add': True,
			'form': form
		}

		return render(request, 'staff/attendance/detail_attendance.html', params)

	else:
		params = {
			'action': reverse('staff_add_attendance'),
			'add': True,
			'form': AttendanceForm()
		}

		return render(request, 'staff/attendance/detail_attendance.html', params)
