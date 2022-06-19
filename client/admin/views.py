from api import admin as admin_api
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import LoginForm, EditStudentForm
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
					if cookie.name == 'token':
						ret.set_cookie(cookie.name, cookie.value, expires=cookie.expires)

				return ret

			elif status_code == 401:
				messages.error(request, response.get('password', 'Authentication failed.'))
				ret = redirect('admin_login')
				ret.cookies['form_id'] = form.cleaned_data.get('id')
				ret.cookies['password'] = form.cleaned_data.get('password')
				return ret

			elif status_code == 404:
				messages.error(request, response.get('id', 'User with given id/email not found.'))
				ret = redirect('admin_login')
				ret.cookies['form_id'] = form.cleaned_data.get('id')
				ret.cookies['form_password'] = form.cleaned_data.get('password')
				return ret

			elif status_code == 400:
				for field in response:
					messages.error(request, response[field])

				return redirect('admin_login')

		else:
			for field in form.errors:
				messages.error(request, form.errors[field])

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

# Students
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def students(request):
	return redirect('admin_students_dashboard')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_dashboard(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to view the dashboard.')
		return redirect('admin_login')

	page_no = request.GET.get('page', 1)
	response, status_code = admin_api.get_all_students(request.COOKIES.get('token'), page_no)
	
	if status_code == 200:
		response['total_pages'] = range(1, response['total_pages'] + 1)
		return render(request, 'admin/students/dashboard.html', response)

	else:
		if status_code == 404:
			messages.error(request, f"Invalid or empty page: {page_no}")
			return redirect('admin_students_dashboard')

		elif status_code == 401:
			if request.META.get('HTTP_REFERER') is None:
				messages.error(request, 'Authentication error: ' + response.get('detail', 'Authentication failed.'))

			return redirect('admin_login')

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
		messages.error(request, 'You must be logged in to edit student details.')
		return redirect('admin_login')

	status_code = admin_api.delete_student(request.COOKIES.get('token'), id)

	if status_code == 200:
		messages.success(request, 'Student deleted successfully.')
		return redirect('admin_students_dashboard')